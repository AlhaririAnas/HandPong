"""
src/core/math_system.py

Manages math task generation, timing, and answer validation.
Generates unique multi-operator equations with results between 0-5.
Uses smaller numbers for easier calculations.
"""

import random
import time


class MathSystem:
    """Coordinates math task generation and answer validation."""

    def __init__(self):
        """Initialize the math task system."""
        self.active = False
        self.task_start_time = 0.0
        self.task_duration = 10.0

        self.equation_string = ""
        self.correct_answer = 0
        
        self.used_equations = set()

    def reset(self):
        """Clear all active tasks and reset for new game session."""
        self.active = False
        self.task_start_time = 0.0
        self.equation_string = ""
        self.correct_answer = 0
        self.used_equations.clear()

    def generate_task(self, current_time):
        """
        Generate a unique random math task with result between 0-5.

        Task types:
        - a op1 b op2 c (e.g. 3 * 2 - 1)
        - a op b (simple cases)

        Args:
            current_time: Current game time in seconds

        Returns:
            True if task generated successfully, False otherwise
        """
        max_attempts = 100
        
        for attempt in range(max_attempts):
            equation_str, result = self._generate_equation()
            
            if equation_str not in self.used_equations and 0 <= result <= 5:
                self.equation_string = equation_str
                self.correct_answer = int(result)
                self.used_equations.add(equation_str)
                
                self.active = True
                self.task_start_time = current_time
                
                return True
        
        return False

    def _generate_equation(self):
        """
        Generate a random equation and calculate its result.

        Returns:
            Tuple of (equation_string, result)
        """
        equation_type = random.choice([
            "two_operands",
            "two_operands", 
            "two_operands",
            "three_operands",
            "three_operands"
        ])

        if equation_type == "two_operands":
            return self._generate_two_operands()
        else:
            return self._generate_three_operands()

    def _generate_two_operands(self):
        """
        Generate simple two-operand equations (a op b).

        Uses small numbers (1-6) for easier math.
        Examples: 3 + 2, 5 - 2, 2 * 2, 6 / 2

        Returns:
            Tuple of (equation_string, result)
        """
        a = random.randint(1, 6)
        b = random.randint(1, 6)
        op = random.choice(["+", "-", "*", "/"])

        if op == "+":
            result = a + b
            display = f"{a} + {b}"
        elif op == "-":
            result = a - b
            display = f"{a} - {b}"
        elif op == "*":
            result = a * b
            display = f"{a} * {b}"
        else:
            if b == 0 or a % b != 0:
                a = b * random.randint(1, 3)
            result = a // b
            display = f"{a} / {b}"

        return (display, result)

    def _generate_three_operands(self):
        """
        Generate three-operand equations (a op1 b op2 c).

        Uses small numbers (1-5) for easier math.
        Examples: 3 * 2 - 1, 5 / 1 + 0, 4 - 2 - 1

        Returns:
            Tuple of (equation_string, result)
        """
        a = random.randint(1, 5)
        b = random.randint(1, 5)
        c = random.randint(1, 4)
        
        op1 = random.choice(["+", "-", "*", "/"])
        op2 = random.choice(["+", "-"])

        intermediate = self._calculate(a, b, op1)
        
        if intermediate is None:
            return self._generate_two_operands()
        
        result = self._calculate(intermediate, c, op2)
        
        if result is None:
            return self._generate_two_operands()

        display = f"{a} {op1} {b} {op2} {c}"
        
        return (display, result)

    def _calculate(self, x, y, op):
        """
        Perform a single calculation.

        Args:
            x: First operand
            y: Second operand
            op: Operator (+, -, *, /)

        Returns:
            Result or None if invalid (e.g., division by zero)
        """
        if op == "+":
            return x + y
        elif op == "-":
            return x - y
        elif op == "*":
            return x * y
        elif op == "/":
            if y == 0 or x % y != 0:
                return None
            return x // y
        
        return None

    def check_answer(self, player_answer):
        """
        Validate player's answer against the correct answer.

        Args:
            player_answer: The player's submitted answer (0-5)

        Returns:
            True if answer is correct, False otherwise
        """
        if not self.active:
            return False

        return int(player_answer) == self.correct_answer

    def get_time_left(self, current_time):
        """
        Calculate remaining time for the current task.

        Args:
            current_time: Current game time in seconds

        Returns:
            Seconds remaining (can be negative if expired)
        """
        if not self.active:
            return 0.0

        elapsed = current_time - self.task_start_time
        return self.task_duration - elapsed

    def get_progress(self, current_time):
        """
        Calculate task progress as value between 0.0 and 1.0.

        Args:
            current_time: Current game time in seconds

        Returns:
            Progress value where 1.0 is fully complete
        """
        if not self.active:
            return 0.0

        elapsed = current_time - self.task_start_time
        return min(1.0, elapsed / self.task_duration)