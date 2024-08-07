import math

def reward_function(params):
    '''
    Reward function for AWS DeepRacer considering dynamic U-turns and incentivizing speed and progress
    '''
    # Read input variables
    track_width = params['track_width']
    distance_from_center = params['distance_from_center']
    steering_angle = abs(params['steering_angle'])
    speed = params['speed']
    all_wheels_on_track = params['all_wheels_on_track']
    progress = params['progress']
    steps = params['steps']
    is_left_of_center = params['is_left_of_center']
    closest_waypoints = params['closest_waypoints']
    waypoints = params['waypoints']
    is_offtrack = params['is_offtrack']

    # Calculate markers
    marker_1 = 0.1 * track_width
    marker_2 = 0.25 * track_width
    marker_3 = 0.5 * track_width

    # Initialize reward
    reward = 1.0

    # Get the indices of the closest waypoints
    prev_wp = closest_waypoints[0]
    next_wp = closest_waypoints[1]

    # Calculate the direction of the turn based on the curvature
    if len(waypoints) > 1:
        prev_wp_pos = waypoints[prev_wp]
        next_wp_pos = waypoints[next_wp]
        future_wp = (next_wp + 1) % len(waypoints)  # Next waypoint after the next
        future_wp_pos = waypoints[future_wp]

        # Calculate vectors
        vector_a = [next_wp_pos[0] - prev_wp_pos[0], next_wp_pos[1] - prev_wp_pos[1]]
        vector_b = [future_wp_pos[0] - next_wp_pos[0], future_wp_pos[1] - next_wp_pos[1]]

        # Calculate the angle between vectors
        dot_product = vector_a[0] * vector_b[0] + vector_a[1] * vector_b[1]
        mag_a = math.sqrt(vector_a[0] ** 2 + vector_a[1] ** 2)
        mag_b = math.sqrt(vector_b[0] ** 2 + vector_b[1] ** 2)
        angle = math.acos(dot_product / (mag_a * mag_b))

        # Check if the angle indicates a sharp turn
        if angle < 0.5:  # Adjusted threshold
            if vector_a[0] * vector_b[1] - vector_a[1] * vector_b[0] > 0:
                # Left U-turn
                if is_left_of_center:
                    reward += 1.5  # Increased reward for correct side in sharp turn
                else:
                    reward -= 0.5  # Reduced penalty for being on the wrong side
            else:
                # Right U-turn
                if not is_left_of_center:
                    reward += 1.5  # Increased reward for correct side in sharp turn
                else:
                    reward -= 0.5  # Reduced penalty for being on the wrong side

    # Reward staying on track
    if all_wheels_on_track and not is_offtrack:
        reward += 1.0

        # Reward based on distance from center
        if distance_from_center <= marker_1:
            reward += 1.0
        elif distance_from_center <= marker_2:
            reward += 0.5
        elif distance_from_center <= marker_3:
            reward += 0.2  # Slightly increased reward for being closer to center

        # Penalize for high steering angles to prevent zig-zagging
        if steering_angle > 20:  # Relaxed angle threshold
            reward *= 0.9  # Reduced penalty to 10%

        # Reward higher speeds
        SPEED_THRESHOLD = 3.5
        if speed > SPEED_THRESHOLD:
            reward += 1.5  # Increased reward for higher speeds
        elif speed > 3.0:
            reward += 0.7  # Slightly increased reward for moderate speeds

        # Reward progress made
        if steps > 0:
            reward += (progress / steps) * 150  # Increased factor to incentivize faster progress
    else:
        reward = 1e-3  # Minimum reward for being off track

    return float(reward)