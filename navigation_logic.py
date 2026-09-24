"""Navigate using forward movement with obstacle avoidance and goal stopping."""
def navigate(perception):
    """Navigate using forward movement with obstacle avoidance and goal stopping."""
    if perception.get('goal_reached', False):
        return "STOP"
    if perception.get('obstacle_ahead', False):
        if not perception.get('obstacle_left', False):
            return "LEFT"
        if not perception.get('obstacle_right', False):
            return "RIGHT"
        return "STOP"
    return "FORWARD"