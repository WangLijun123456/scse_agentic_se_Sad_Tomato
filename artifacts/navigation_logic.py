"""
Navigation logic based on the Planner Agent's validated plan, prioritizing goal movement while avoiding obstacles and stopping when all directions are blocked.
"""

def navigate(perception):
    # Check each decision in the order specified in the plan
    if perception.get('goal_ahead', False) and not perception.get('front_blocked', False):
        return "FORWARD"
    if perception.get('goal_on_left', False) and not perception.get('left_blocked', False):
        return "LEFT"
    if perception.get('goal_on_right', False) and not perception.get('right_blocked', False):
        return "RIGHT"
    if perception.get('front_blocked', False) and not perception.get('left_blocked', False):
        return "LEFT"
    if perception.get('front_blocked', False) and not perception.get('right_blocked', False):
        return "RIGHT"
    if perception.get('front_blocked', False) and perception.get('left_blocked', False) and perception.get('right_blocked', False):
        return "STOP"
    # Default case: continue moving forward if no conditions are met
    return "FORWARD"

def decide_next_move(state):
    """Decide the next action based on current state and navigation plan."""
    return navigate(state)