"""
Research Topics
ArrayList, Recursion, and Queue & Priority Queue content
Updated with Professor's "Stop Sign" and "Suitcase" methodologies
Bug fixes: self-answering pattern and reflection loop corrected across all topics
"""

from dataclasses import dataclass
from typing import List, Dict


# content/research_topics.py

class ResearchTopic:
    """
    Holds ALL topic-specific content AND step-specific instructional guidance.
    StepGuide becomes a generic engine that simply pulls from this.
    """

    def __init__(
        self,
        key: str,
        name: str,
        difficulty: str,
        concept: str,
        key_points: list[str],
        metaphor_prompt: str,
        agent_crisis: str,
        agent_solution: str,
        code_focus: str,
        instructions: dict[str, str],
    ):
        self.key = key
        self.name = name
        self.difficulty = difficulty
        self.concept = concept
        self.key_points = key_points
        self.metaphor_prompt = metaphor_prompt
        self.agent_crisis = agent_crisis
        self.agent_solution = agent_solution
        self.code_focus = code_focus
        self.instructions = instructions

    def instructions_for(self, step_name: str) -> str:
        """
        Return the instruction block for a given scaffold step.
        """
        return self.instructions.get(step_name, "")


# -------------------------------------------------------------------------
# TOPIC 1: ARRAYLIST (The Suitcase / Dynamic Resizing)
# -------------------------------------------------------------------------
ARRAYLIST_TOPIC = ResearchTopic(
    key="arraylist",
    name="Dynamic ArrayList",
    difficulty="easy",
    concept=(
        "An abstraction that allows an array to feel 'infinite' by secretly "
        "replacing a full underlying array with a larger one."
    ),
    key_points=[
        "Java arrays are fixed size; ArrayList feels 'infinite'.",
        "When full, it creates a new, larger array (Hidden Work).",
        "It copies all old items to the new array.",
        "Then it points the reference variable to the new array.",
        "The crisis: what happens when the suitcase (array) is full?"
    ],
    metaphor_prompt=(
        "Think about an ArrayList like a suitcase. If your suitcase is full, "
        "but you bought more clothes, what do you do? You have to buy a bigger "
        "suitcase and move ALL your clothes over to the new one before you can "
        "add the new items."
    ),
    agent_crisis=(
        "Java arrays are fixed size. If our array has 4 slots and they are all "
        "full, and we try to add a 5th element, the program crashes. How do we "
        "fix this without changing the nature of arrays?"
    ),
    agent_solution=(
        "We need to create a new, larger array, copy everything over, and then "
        "switch to using that new array (e.g., internalArray = newArray)."
    ),
    code_focus=(
        "The resizing logic: checking if full, creating newArray, copying items, "
        "and reassigning internalArray."
    ),
    instructions={
        "initial_metaphor": (
            "Start with this metaphor:\n"
            "\"{metaphor_prompt}\"\n"
            "Then ask the student what this reminds them of from their own life.\n"
            "STOP. Do NOT continue. Wait for their response."
        ),
        "student_metaphor": (
            "1. Briefly acknowledge the student's metaphor or example.\n"
            "2. Pivot to the conflict: {agent_crisis}\n"
            "3. Ask: 'Ready to see how this works visually?'\n"
            "STOP. Do NOT answer or explain further. Wait for the student."
        ),
        "visual_diagram": (
            "The visual was already shown. Do NOT show it again.\n"
            "Ask ONE question only: 'What part of this diagram is most helpful?'\n"
            "STOP. Wait for their answer. Keep your response under 50 words total."
        ),
        "code_structure": (
            "Show the RESIZE method — the internal mechanism.\n"
            "Highlight the copy loop: for (int i = 0; i < size; i++)\n"
            "Explain: This is O(n) — every element must be copied.\n"
            "Then ask ONE question: 'If we have 1000 elements, how expensive is this copy?'\n"
            "STOP. Do NOT answer. Wait for the student.\n"
            "Do NOT show usage code. Show the INTERNAL implementation only."
        ),
        "code_usage": (
            "Show usage code:\n"
            "ArrayList<String> items = new ArrayList<>();\n"
            "items.add(\"A\");\n"
            "Briefly explain that resize happens automatically behind the scenes.\n"
            "Then ask ONE question: 'What happens performance-wise when we add 1000 items?'\n"
            "STOP. Do NOT answer. Wait for the student.\n"
            "Do NOT re-explain resizing. Student already knows this."
        ),
        "worked_example": (
            "Walk through a concrete example of ArrayList resizing.\n"
            "Ask ONE check question about capacity vs size.\n"
            "STOP. Wait for the student's answer."
        ),
        "guided_problem": (
            "Present a guided problem with blanks for initializing an ArrayList and adding elements.\n"
            "Ask the student to fill in the blanks.\n"
            "STOP. Wait for their response."
        ),
        "practice": (
            "Ask ONE practice question about when resizing occurs.\n"
            "Example: 'If capacity is 8 and size is 7, what happens when we add 2 elements?'\n"
            "STOP. Wait for their answer before giving any feedback.\n"
            "Give brief feedback only after they respond. Then move to reflection."
        ),
        "reflection": (
            "Ask the student to summarize what they learned in 1-2 sentences.\n"
            "STOP. Wait for their response.\n"
            "When they respond, accept ANY reasonable summary that includes:\n"
            "  - ArrayList can grow dynamically, AND\n"
            "  - resizing has a cost (O(n) copy).\n"
            "If their summary covers both ideas even loosely, affirm it and END the session.\n"
            "Do NOT ask them to summarize again after they already have.\n"
            "Do NOT repeat the closing question.\n"
            "Do NOT ask for more detail.\n"
            "Once confirmed, say something like: 'Exactly right. Great work today!' and stop."
        ),
    }
)


# -------------------------------------------------------------------------
# TOPIC 2: RECURSION (The Stop Sign / Base Case)
# -------------------------------------------------------------------------
RECURSION_TOPIC = ResearchTopic(
    key="recursion",
    name="Recursion: The Stop Sign (Base Case)",
    difficulty="medium",
    concept=(
        "A method that solves a problem by calling a smaller version of itself "
        "until it reaches a trivial solution (the base case)."
    ),
    key_points=[
        "Recursion solves a problem by calling a smaller version of itself.",
        "The base case is the 'Stop Sign' where recursion ends.",
        "The recursive case does work and calls the function again.",
        "The call stack fills up with pending recursive calls.",
    ],
    metaphor_prompt=(
        "Think of recursion like a process that keeps stepping down a staircase "
        "until it reaches the bottom step, where it can finally stop and turn around."
    ),
    agent_crisis=(
        "If we write a recursive function without an if-statement or base case, "
        "and we call it, it calls itself, which calls itself, and so on. When "
        "does it actually return a value?"
    ),
    agent_solution=(
        "We must define a base case—the 'Stop Sign'—that returns a simple, "
        "hard-coded value, and ensure each recursive call moves us closer to that base case."
    ),
    code_focus=(
        "Distinguishing the base case from the recursive case and ensuring that "
        "each call reduces n so we eventually hit the base case."
    ),
    instructions={
        "initial_metaphor": (
            "Start with a simple metaphor for recursion, such as walking down a "
            "staircase one step at a time until you reach the bottom.\n"
            "Use this to hint that there must be a final, simplest step where you stop.\n"
            "Then ask the student if this reminds them of anything.\n"
            "STOP. Do NOT continue. Wait for their response."
        ),
        "student_metaphor": (
            "1. Acknowledge the student's metaphor or example.\n"
            "2. Pivot to the crisis: {agent_crisis}\n"
            "3. Ask: 'Ready to see how the call stack works visually?'\n"
            "STOP. Do NOT answer or explain further. Wait for the student."
        ),
        "visual_diagram": (
            "The student has seen a visual diagram showing the recursive call stack.\n"
            "Briefly explain in 2-3 sentences:\n"
            "  - Each recursive call gets added to the stack, building up.\n"
            "  - The base case stops the recursion.\n"
            "  - The stack then unwinds, each call returning its value.\n"
            "Then ask ONE question: 'Can you see how the stack builds up and then unwinds?'\n"
            "STOP. Wait for the student's response before moving on."
        ),
        "code_structure": (
            "Show a recursive factorial function WITHOUT a base case first.\n"
            "Ask ONE question: 'If I call this version, when does it stop calling itself?'\n"
            "STOP. Wait for the student's answer.\n"
            "Only AFTER they respond: introduce the proper structure with the base case.\n"
            "Do NOT pre-answer the question. Do NOT show the fix before they guess."
        ),
        "code_usage": (
            "Show how the method is called from user code:\n"
            "System.out.println(factorial(3)); // Outputs: 6\n"
            "Explain briefly: The base case is what allows it to successfully calculate and return 6.\n"
            "Then ask ONE question: 'What error or crash happens if we remove or forget that base case?'\n"
            "STOP. Do NOT answer. Do NOT explain. Do NOT ask any follow-up questions.\n"
            "When the student answers — ANY answer mentioning infinite loop, stack overflow, "
            "or crashing — accept it immediately and move to the next step.\n"
            "Do NOT repeat this question under any circumstances."
        ),
        "worked_example": (
            "Walk through this simple, concrete worked example of recursion:\n\n"
            "public static void countDown(int n) {\n"
            "    if (n <= 0) {  // Base Case: Stop sign!\n"
            "        System.out.println(\"Blastoff!\");\n"
            "        return;\n"
            "    }\n"
            "    System.out.println(n);\n"
            "    countDown(n - 1);  // Recursive call: moves closer to 0\n"
            "}\n\n"
            "Explain the two key pieces clearly and simply:\n"
            "1. The Base Case: `if (n <= 0)` is our stop sign. When n reaches 0, it prints 'Blastoff!' and stops.\n"
            "2. The Recursive Call: `countDown(n - 1)` calls itself with n - 1, stepping down toward 0.\n\n"
            "Ask this ONE simple check question:\n"
            "'Looking at this code, what number does n need to reach to hit the stop sign and stop the countdown?'\n"
            "STOP. Wait for the student's answer.\n"
            "Expected answer: 0 (or n <= 0). Accept any answer mentioning 0 or the stop sign."
        ),
        "guided_problem": (
            "Present this guided problem for printStars:\n\n"
            "public static void printStars(int count) {\n"
            "    if (count == 0) {\n"
            "        return; // Base case: stop sign\n"
            "    }\n"
            "    System.out.print(\"*\");\n"
            "    // Recursive call\n"
            "    printStars(____); // What goes in the blank?\n"
            "}\n\n"
            "Ask the student this simple guided question:\n"
            "'To move closer to our base case of count == 0 and avoid looping forever, should we call printStars(count) or printStars(count - 1)?'\n"
            "STOP. Wait for their response.\n"
            "Expected answer: printStars(count - 1) or (count - 1) or similar.\n"
            "Validate their answer warmly: explain that count - 1 reduces the number each time so it reaches the stop sign (0), whereas printStars(count) would never stop and cause an infinite loop. Then ask if they are ready for the practice problem."
        ),
        "practice": (
            "Tell the student: 'Here is our factorial function:'\n"
            "Show the code without any labels or comments identifying the parts (to avoid giving away the answer):\n"
            "  def factorial(n):\n"
            "      if n == 1:\n"
            "          return 1\n"
            "      else:\n"
            "          return n * factorial(n - 1)\n\n"
            "Ask ONE question: 'Which line is the base case and which is the recursive case?'\n"
            "STOP. Wait for their answer before giving any feedback.\n"
            "After they answer, give brief confirmation and move to reflection."
        ),
        "reflection": (
            "Ask: 'How would you explain recursion to someone who has never seen it?'\n"
            "STOP. Wait for their answer.\n"
            "When they respond, accept ANY reasonable summary that includes:\n"
            "  - a method calling itself, AND\n"
            "  - a base case stopping the recursion.\n"
            "If their summary covers both ideas even loosely, affirm it and END the session.\n"
            "Do NOT ask them to summarize again after they already have.\n"
            "Do NOT repeat the closing question.\n"
            "Do NOT ask for more detail.\n"
            "Once confirmed, say something like: 'Exactly right. Great work today!' and stop."
        ),
    }
)


# -------------------------------------------------------------------------
# TOPIC 3: QUEUE & PRIORITY QUEUE (The Line / The ER)
# -------------------------------------------------------------------------
QUEUE_TOPIC = ResearchTopic(
    key="queue",
    name="Queue & Priority Queue",
    difficulty="medium",
    concept=(
        "A Queue serves elements in arrival order (FIFO). A Priority Queue "
        "breaks that rule — the highest-priority element always exits first, "
        "regardless of when it arrived."
    ),
    key_points=[
        "FIFO: First In, First Out — a regular Queue preserves arrival order.",
        "offer() adds to the back; poll() removes from the front.",
        "No random access — you can only interact with the front and back.",
        "A Priority Queue ignores arrival order — priority wins.",
        "Java's PriorityQueue uses a min-heap: smallest value exits first.",
        "Custom ordering requires a Comparator to flip or define priority.",
        "The crisis: what happens when arrival order isn't fair enough?",
    ],
    metaphor_prompt=(
        "Think about a Queue like the line at a coffee shop — first in, first "
        "out, nobody cuts. But a Priority Queue is like an ER triage desk. "
        "It doesn't matter who arrived first. The most critical patient goes "
        "back immediately, even if they walked in last."
    ),
    agent_crisis=(
        "A regular Queue is fair by arrival order. But what if a low-priority "
        "task is sitting at the front while a critical one just arrived? "
        "Strict FIFO fails us. How do we serve the most important element "
        "next, efficiently?"
    ),
    agent_solution=(
        "For a regular Queue, Java's LinkedList gives O(1) offer() and poll() "
        "with no shifting. For priority ordering, Java's PriorityQueue uses a "
        "min-heap so poll() always returns the highest-priority element in O(log n)."
    ),
    code_focus=(
        "Queue interface methods (offer, poll, peek) and PriorityQueue behavior — "
        "default min-heap ordering and custom Comparators."
    ),
    instructions={
        "initial_metaphor": (
            "Start with this metaphor:\n"
            "\"{metaphor_prompt}\"\n"
            "Ask: 'Can you think of a real situation where arrival order is fair, "
            "and another where priority should override it?'\n"
            "STOP. Do NOT continue. Wait for their response."
        ),
        "student_metaphor": (
            "1. Acknowledge the student's examples.\n"
            "2. Pivot to the conflict: {agent_crisis}\n"
            "3. Ask: 'Ready to see both structures side by side visually?'\n"
            "STOP. Do NOT answer or explain further. Wait for the student."
        ),
        "visual_diagram": (
            "The visual was already shown. Do NOT show it again.\n"
            "Ask ONE question only: 'What's the key difference between the two "
            "structures in terms of what exits first?'\n"
            "STOP. Keep your response under 50 words. Wait for their answer."
        ),
        "code_structure": (
            "Show the regular Queue code:\n"
            "  Queue<String> line = new LinkedList<>();\n"
            "  line.offer(\"Alice\");\n"
            "  line.offer(\"Bob\");\n"
            "  line.poll(); // 'Alice' — first in, first out\n\n"
            "Note: unlike ArrayList, there is no get(index) — "
            "you can only touch the front (Head) and back (Tail).\n\n"
            "Then show PriorityQueue:\n"
            "  PriorityQueue<Integer> pq = new PriorityQueue<>();\n"
            "  pq.offer(5);\n"
            "  pq.offer(1);\n"
            "  pq.offer(3);\n"
            "  pq.poll(); // returns 1 — not 5!\n\n"
            "Ask ONE question: 'Why did 1 come out even though 5 was added first?'\n"
            "STOP. Do NOT answer. Wait for the student."
        ),
        "code_usage": (
            "TERMINOLOGY: Always use Java method names — offer(), poll(), peek(). "
            "Never say 'enqueue' or 'dequeue' — students must learn the actual API.\n\n"
            "Show the custom Comparator example:\n"
            "  PriorityQueue<int[]> tasks = new PriorityQueue<>(\n"
            "      (a, b) -> a[1] - b[1]\n"
            "  );\n"
            "  tasks.offer(new int[]{1, 3});\n"
            "  tasks.offer(new int[]{2, 1});\n"
            "  tasks.poll(); // task 2 wins — priority 1\n\n"
            "Ask ONE question: 'When would you use a regular Queue vs. a PriorityQueue?'\n"
            "STOP. Do NOT answer. Wait for the student."
        ),
        "worked_example": (
            "TERMINOLOGY: Always use Java method names — offer(), poll(), peek().\n\n"
            "Walk through this concrete worked example of a regular Queue:\n\n"
            "Queue<String> printJobs = new LinkedList<>();\n"
            "printJobs.offer(\"Document_A\");\n"
            "printJobs.offer(\"Document_B\");\n\n"
            "System.out.println(printJobs.poll()); // Prints 'Document_A' (FIFO order)\n"
            "System.out.println(printJobs.peek()); // Peeks at 'Document_B' without removing it\n\n"
            "Explain briefly:\n"
            "- offer() adds to the back of the queue.\n"
            "- poll() removes and returns the front item.\n"
            "- peek() inspects the front item without removing it.\n\n"
            "Then ask ONE check question: 'If we call printJobs.poll() right after peek(), which document comes out and how many remain in the queue?'\n"
            "STOP. Wait for the student's answer."
        ),
        "guided_problem": (
            "TERMINOLOGY: Always use Java method names — offer(), poll(), peek().\n\n"
            "Present this guided problem for an Emergency Room PriorityQueue:\n\n"
            "// Severity: 1 = Critical, 5 = Minor (Java min-heap: lowest number = highest priority)\n"
            "PriorityQueue<Integer> erQueue = new PriorityQueue<>();\n"
            "erQueue.offer(5); // Minor headache\n"
            "erQueue.offer(1); // Urgent trauma\n\n"
            "// TODO: Fill in the blank to get and remove the most urgent patient\n"
            "int nextPatient = erQueue.____(); // TODO 1: method name\n\n"
            "Ask the student: 'What method replaces the blank, and will nextPatient be 1 or 5?'\n"
            "STOP. Wait for their response.\n"
            "Expected: poll(), returns 1 (because min-heap gives the smallest value first).\n"
            "Accept any close answer, validate it warmly, explain briefly, and prepare for practice."
        ),
        "practice": (
            "TERMINOLOGY: Always use Java method names — offer(), poll(), peek(). "
            "Never say 'enqueue' or 'dequeue' — students must learn the actual API.\n\n"
            "Ask ONE practice question:\n"
            "'If you add 10, 4, 7, 2 to a PriorityQueue and call poll() "
            "three times, what comes out and in what order? Would a regular "
            "Queue give you the same result? Why or why not?'\n"
            "STOP. Wait for their answer before giving any feedback."
        ),
        "reflection": (
            "Ask the student to summarize both structures in 2-3 sentences.\n"
            "STOP. Wait for their response.\n"
            "When they respond, accept ANY reasonable summary that includes:\n"
            "  - Queue = FIFO / arrival order, AND\n"
            "  - PriorityQueue = priority wins / arrival order ignored.\n"
            "If their summary covers both ideas even loosely, affirm it and END the session.\n"
            "Do NOT ask them to summarize again after they already have.\n"
            "Do NOT repeat the closing question.\n"
            "Do NOT ask for more detail.\n"
            "Once confirmed, say something like: 'Exactly right. Great work today!' and stop."
        ),
    }
)


RESEARCH_TOPICS = {
    'arraylist': ARRAYLIST_TOPIC,
    'recursion': RECURSION_TOPIC,
    'queue': QUEUE_TOPIC
}


def get_research_topic(topic_key: str) -> ResearchTopic:
    if topic_key not in RESEARCH_TOPICS:
        for topic in RESEARCH_TOPICS.values():
            if topic.name == topic_key:
                return topic
        raise ValueError(f"Topic '{topic_key}' not found")
    return RESEARCH_TOPICS[topic_key]