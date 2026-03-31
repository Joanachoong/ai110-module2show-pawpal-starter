# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.

My initial UML design separated planning data from planning logic. I created both a Schedule class and a Scheduler class, but at that stage they had overlapping responsibilities. I also duplicated task-adding behavior between Owner and Schedule, which made the design less clear.

- What classes did you include, and what responsibilities did you assign to each?

There are the **5 classes** in your UML class diagram:

1. **Dashboard** — display all the information 
2. **Scheduler** — applies rules and constraints to choose and order tasks.
3. **Owner** — stores owner information and preferences, and provides constraints such as available time.
4. **Pet** — stores pet profile details such as name, species, and care-related attributes.
5. **Task** — represents a care task with fields like title, duration, and priority.


**b. Design changes**

- Did your design change during implementation? Yes

- If yes, describe at least one change and why you made it.
Given that I merged schedule and scheduler into one class in the end given they share the same feature . Other than that, I removed the duplicate fucntion that was shown in both Owner and schedualer class.  

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
I added constraint based on due date , completion status and pet name 

- How did you decide which constraints mattered most?
I proritized due date as the first filter because this user will be more avware of which task should be complete by today 

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
Date is not given in the task, when user select task as daily or weekly , it does not show the date of the task

- Why is that tradeoff reasonable for this scenario?
Given that user prorities is to know what is today task , date is a redundant value

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

I used ai mainly to help me brainstorm , espcecially how to refractor the schedule and task relationship. Given the first try the relationship between task and scehedule was messy and have many bug. 

- What kinds of prompts or questions were most helpful?
The most usefull prompt is giving ai specific library that and prompt them to refine or update the code using the following classes given.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
AI first suggestion on having schdule and scheduler feature , given it is redunadnt and not necessary

- How did you evaluate or verify what the AI suggested?
I will ask AI to give me a plan and show me the reasonning they add this feature . Then , I evaluate the result based on my primary goals and the features I want to build . In the meantime , I consisitenly review th UML diagram to make sure the AI did not maje drastic changes to breaks the connection that I have set in the beginning.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
I tested  Basic task lifecycle behavior , Conflict and duplicate detection , Sorting correctness for scheduling,  Recurrence logic on completion, Query/filter and
plus edge behavior when a pet has no tasks.

- Why were these tests important?
To ensure all the performace that user might conduct are tested and reduce bugs 

**b. Confidence**

- How confident are you that your scheduler works correctly?
4/5

- What edge cases would you test next if you had more time?
No

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

This project has taught me how to refine AI prompt, using test case is one of the best way to eveluate still on the right track.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would refine I would add additional feature for user to add weekly task and set a weekly to do task.


**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
AI does not have the full capabiluty to conduct system design , there are many human interaction that are not palced into consideration during the first run , consistent refinemnet and personal evaluation is important to prevent system error when scale get more bigger and complex.
