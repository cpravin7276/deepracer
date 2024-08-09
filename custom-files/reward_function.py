import math

def reward_function(params):
    '''
    Combined reward function for AWS DeepRacer optimized for Rose Raceway (counterclockwise).
    Encourages correct positioning for upcoming turns, rewards maintaining high speeds,
    and specifically rewards well-executed turns while penalizing high speed for U-turns.
    '''
    # Track parameters
    track_width = params['track_width']
    distance_from_center = params['distance_from_center']
    steering_angle = abs(params['steering_angle'])
    speed = params['speed']
    all_wheels_on_track = params['all_wheels_on_track']
    progress = params['progress']
    steps = params['steps']
    is_offtrack = params['is_offtrack']

    # Markers for distance from center
    marker_1 = 0.1 * track_width
    marker_2 = 0.2 * track_width
    marker_3 = 0.4 * track_width

    # Initialize reward
    reward = 1.0

    # Penalize going off-track heavily
    if is_offtrack:
        return 1e-3

    # Reward for keeping all wheels on track
    if all_wheels_on_track:
        reward += 1.0

        # Reward based on distance from center
        if distance_from_center <= marker_1:
            reward += 1.2
        elif distance_from_center <= marker_2:
            reward += 0.8
        elif distance_from_center <= marker_3:
            reward += 0.5

        # Penalize for high steering angles to prevent zig-zagging
        if steering_angle > 15:
            reward *= 0.7

        # Penalize sharp turns at high speed
        HIGH_SPEED_THRESHOLD = 3.0
        SHARP_TURN_THRESHOLD = 15  # degrees
        if steering_angle > SHARP_TURN_THRESHOLD and speed > HIGH_SPEED_THRESHOLD:
            reward *= 0.4
        
        U_TURN_SPEED_PENALTY = 0.4
        if is_U_turn and speed > 2.0:
            reward *= U_TURN_SPEED_PENALTY

        # Reward for maintaining a good speed
        SPEED_THRESHOLD = 3.5
        if speed >= SPEED_THRESHOLD:
            reward += 1.5
        elif speed >= 3.0:
            reward += 1.0
        elif speed >= 2.5:
            reward += 0.8
        elif speed >= 2.0:
            reward += 0.5

        # Reward progress efficiently
        if steps > 0:
            reward += (progress / steps) * 150

    else:
        reward = 1e-3  # Minimum reward for being off track

    return float(reward)
