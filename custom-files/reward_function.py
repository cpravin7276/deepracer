import math

def reward_function(params):
    '''
    Optimized reward function for AWS DeepRacer on Rose Raceway (counterclockwise).
    Focuses on minimizing lap time by promoting the optimal racing line, handling turns efficiently,
    maintaining high speed, and managing U-turns.
    '''

    # Extract necessary parameters
    track_width = params['track_width']
    distance_from_center = params['distance_from_center']
    speed = params['speed']
    all_wheels_on_track = params['all_wheels_on_track']
    waypoints = params['waypoints']
    closest_waypoints = params['closest_waypoints']
    heading = params['heading']
    steering_angle = abs(params['steering_angle'])
    progress = params['progress']
    steps = params['steps']
    is_offtrack = params['is_offtrack']
    is_left_of_center = params['is_left_of_center']

    # Start with a small base reward
    reward = 1.0

    # Handle off-track cases
    if not all_wheels_on_track or is_offtrack:
        return 1e-3

    # Determine position markers
    marker_1 = 0.1 * track_width
    marker_2 = 0.2 * track_width
    marker_3 = 0.4 * track_width

    # Reward for staying near the centerline
    if distance_from_center <= marker_1:
        reward += 1.5
    elif distance_from_center <= marker_2:
        reward += 1.0
    elif distance_from_center <= marker_3:
        reward += 0.5
    else:
        reward += 0.1  # Minimal reward for being too far from the center

    # Calculate track direction
    next_waypoint = waypoints[closest_waypoints[1]]
    prev_waypoint = waypoints[closest_waypoints[0]]
    track_direction = math.atan2(next_waypoint[1] - prev_waypoint[1], next_waypoint[0] - prev_waypoint[0])
    track_direction = math.degrees(track_direction)

    # Calculate the direction difference between track and heading
    direction_diff = abs(track_direction - heading)
    if direction_diff > 180:
        direction_diff = 360 - direction_diff

    # Penalize large deviations from the optimal direction
    DIRECTION_THRESHOLD = 5.0
    if direction_diff > DIRECTION_THRESHOLD:
        reward *= 0.5

    # Encourage maximum speed where direction alignment is good
    HIGH_SPEED_THRESHOLD = 3.5
    LOW_SPEED_THRESHOLD = 2.0

    if direction_diff < DIRECTION_THRESHOLD:
        if speed >= HIGH_SPEED_THRESHOLD:
            reward += 2.0
        elif speed >= LOW_SPEED_THRESHOLD:
            reward += 1.0
        else:
            reward += 0.5  # Small reward for keeping some speed

    # Optimize for steering angles (encourage smooth driving)
    ABS_STEERING_THRESHOLD = 10.0
    if abs(steering_angle) < ABS_STEERING_THRESHOLD:
        reward += 0.5
    else:
        reward *= 0.8

    # Further reward for sticking to the optimal racing line
    racing_line_bonus = 1.0
    if distance_from_center <= marker_1 and direction_diff < DIRECTION_THRESHOLD:
        reward += racing_line_bonus
    # Adjust reward for sharp corners and U-turns
    turn_radius = abs(prev_waypoint[0] - next_waypoint[0]) + abs(prev_waypoint[1] - next_waypoint[1])
    SHARP_TURN_THRESHOLD = 15  # degrees

    if turn_radius < 0.5 * track_width:  # Sharp turn
        if speed < HIGH_SPEED_THRESHOLD:
            reward += 1.0  # Reward slowing down for sharp turns
        else:
            reward *= 0.6  # Penalize high speed in sharp turns
    else:  # Gentle curve or straight
        if speed >= HIGH_SPEED_THRESHOLD:
            reward += 1.0  # Encourage high speed on gentle curves and straights

    # Additional penalty for U-turns if speed is too high
    U_TURN_SPEED_PENALTY = 0.4
    if turn_radius < 0.3 * track_width and speed > 2.0:  # Identifying a U-turn scenario
        reward *= U_TURN_SPEED_PENALTY

    # Recovery bonus: Encourage the car to get back to the optimal path if it's deviating
    if distance_from_center > marker_3:
        reward += 0.5  # Reward for correcting course towards the center

    # Reward for fast lap completion
    REWARD_FOR_FAST_COMPLETION = 100
    if progress == 100:
        reward += REWARD_FOR_FAST_COMPLETION / (steps + 1)  # Adding +1 to avoid division by zero

    # Reward progress efficiently
    if steps > 0:
        reward += (progress / steps) * 150

    return float(reward)
