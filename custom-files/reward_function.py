import math

def reward_function(params):
    '''
    Reward function for AWS DeepRacer ensuring efficiency and preventing off-track behavior,
    with penalties for sharp turns at high speeds.
    '''
    # Read input variables
    track_width = params['track_width']
    distance_from_center = params['distance_from_center']
    steering_angle = abs(params['steering_angle'])
    speed = params['speed']
    all_wheels_on_track = params['all_wheels_on_track']
    progress = params['progress']
    steps = params['steps']
    is_offtrack = params['is_offtrack']

    # Calculate markers for distance from center
    marker_1 = 0.1 * track_width
    marker_2 = 0.25 * track_width
    marker_3 = 0.5 * track_width

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
            reward += 1.0
        elif distance_from_center <= marker_2:
            reward += 0.5
        elif distance_from_center <= marker_3:
            reward += 0.1

        # Penalize for high steering angles to prevent zig-zagging
        if steering_angle > 15:
            reward *= 0.8

        # Penalize sharp turns at high speed
        HIGH_SPEED_THRESHOLD = 3.5
        SHARP_TURN_THRESHOLD = 20  # degrees
        if steering_angle > SHARP_TURN_THRESHOLD and speed > HIGH_SPEED_THRESHOLD:
            reward *= 0.5  # This multiplier can be adjusted as needed

        # Reward higher speeds with a threshold
        SPEED_THRESHOLD = 3.0
        if speed > SPEED_THRESHOLD:
            reward += 1.0
        elif speed > 2.5:
            reward += 0.5

        # Reward progress made efficiently
        if steps > 0:
            reward += (progress / steps) * 100
    else:
        reward = 1e-3  # Minimum reward for being off track

    return float(reward)
