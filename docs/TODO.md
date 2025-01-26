# TODO

Here's a detailed plan to integrate the agent framework with your Todoist ingestion pipeline today, focusing on getting the SoMinE agent to process tasks:

**Phase 1: Preparation and Setup (Estimated Time: 30-45 minutes)**

1. **Environment Check:**

   - Ensure your development environment is active and all dependencies from `pyproject.toml` are installed. You can do this by running `poetry install` in your project's root directory.
   - Verify that your `TODOIST_API_TOKEN` is correctly set in your `.env` file.

2. **Code Review and Refresher:**

   - Quickly review the following files to refresh your memory of the current structure:
     - `src/aerith_aerith_ingestion/main.py`: Understand the main entry point and how `TodoistIngestion` is used.
     - `src/aerith_aerith_ingestion/aerith_ingestion.py`: Focus on the `process_tasks` method, as this is where we'll integrate the agent.
     - `src/aerith_aerith_ingestion/agents/somine.py`: Understand the `SoMinEAgent`'s `process` method and its dependencies (Inquiry, Instruction, Reflection processors, StateManager, InsightManager).
     - `src/aerith_aerith_ingestion/agents/processors.py`: Review the default implementations of the processors. You might need to customize these later.
     - `src/aerith_aerith_ingestion/agents/managers.py`: Understand how `SoMinEStateManager` and `InsightManager` work.

3. **Logging Setup:**
   - Ensure that logging is properly configured. You're using `loguru`, which is already set up in `main.py`.
   - Decide on the appropriate logging levels for different parts of the integration process (e.g., `debug` for detailed agent steps, `info` for general flow, `error` for exceptions).

**Phase 2: Agent Integration (Estimated Time: 1-2 hours)**

1. **Create Agent Instances:**

   - In `aerith_ingestion.py`, modify the `TodoistIngestion` class to initialize the necessary agent components within its `__init__` method:

   ```python:src/aerith_aerith_ingestion/aerith_ingestion.py
   # ... other imports ...
   from aerith_aerith_ingestion.agents import (
       SoMinEAgent,
       SoMinEStateManager,
       InsightManager,
       DefaultInquiryProcessor,
       DefaultInstructionProcessor,
       DefaultReflectionProcessor,
   )

   class TodoistIngestion:
       def __init__(self, api_client: Optional[TaskAPI] = None, storage: Optional[TaskStorage] = None):
           # ... existing code ...

           # Initialize agent components
           self.state_manager = SoMinEStateManager()
           self.insight_manager = InsightManager(state=self.state_manager.state)
           self.inquiry_processor = DefaultInquiryProcessor(self.insight_manager)
           self.instruction_processor = DefaultInstructionProcessor(self.insight_manager)
           self.reflection_processor = DefaultReflectionProcessor(self.insight_manager)
           self.agent = SoMinEAgent(
               inquiry_processor=self.inquiry_processor,
               instruction_processor=self.instruction_processor,
               reflection_processor=self.reflection_processor,
               state_manager=self.state_manager,
               insight_manager=self.insight_manager,
           )

       # ... rest of the class ...
   ```

2. **Integrate Agent Processing:**

   - Modify the `process_tasks` method in `aerith_ingestion.py` to pass each task to the `SoMinEAgent` for processing:

   ```python:src/aerith_aerith_ingestion/aerith_ingestion.py
   class TodoistIngestion:
       # ...
       async def process_tasks(self) -> None:
           """Process all tasks from Todoist."""
           logger.info("Starting task processing")

           # Get all tasks
           tasks = self.api.get_all_tasks()
           logger.info(f"Retrieved {len(tasks)} tasks")

           # Process each task
           for task in tasks:
               try:
                   # Get complete task data
                   task_data, original_response = self.api._get_task_and_response(task.id)

                   # Create and save document
                   task_doc = TaskDocument.create(task_data, original_response)
                   self.storage.save_task(task_doc)
                   logger.info(f"Processed task {task.id}")

                   # Pass task data to the agent
                   agent_input = {
                       "task_id": task.id,
                       "content": task.content,
                       "description": task_data.description,
                       "project_id": task.project_id,
                       "due": task.due.to_dict() if task.due else None,
                       "original_response": original_response,
                   }
                   agent_response = await self.agent.process(agent_input)
                   logger.info(f"Agent response for task {task.id}: {agent_response}")

               except Exception as e:
                   logger.error(f"Failed to process task {task.id}: {str(e)}")
                   continue

           logger.info("Completed task processing")
   ```

**Phase 3: Initial Testing and Debugging (Estimated Time: 1-2 hours)**

1. **Run the Ingestion:**

   - Execute the `main.py` script to start the ingestion process.
   - Observe the logs carefully. You should see the agent's processing steps (Inquiry, Instruction, Reflection, Final) for each task.

2. **Basic Debugging:**

   - If you encounter errors, use the logs and potentially a debugger to identify the source.
   - Common issues might include:
     - Incorrect data being passed to the agent.
     - Exceptions within the agent's processors.
     - Problems with state management.

3. **Verify Agent Output:**
   - At this stage, focus on ensuring that the agent is receiving the task data, processing it through its phases, and producing some output (even if it's not yet perfectly refined).
   - Check the logs to see the `AgentResponse` for each task.

**Phase 4: Refinement and Customization (Estimated Time: 1-2 hours)**

1. **Customize Processors (if needed):**

   - If the default processors are not generating the desired questions, instructions, or reflections, create custom implementations of the `InquiryProcessorInterface`, `InstructionProcessorInterface`, and `ReflectionProcessorInterface`.
   - Replace the default processors in `TodoistIngestion.__init__` with your custom ones.

2. **Handle Agent Output:**

   - Decide what to do with the `AgentResponse`. You have several options:
     - **Store it with the task:** Modify `TaskDocument` to include a field for the agent's output and save it along with the task data.
     - **Log it:** For now, simply logging the output might be sufficient.
     - **Process it further:** You could potentially use the agent's output to:
       - Update the task in Todoist (e.g., add comments based on the agent's analysis).
       - Trigger other actions in your system.

3. **Iterate and Improve:**
   - Run the ingestion process multiple times, observing the agent's behavior and refining the processors or output handling as needed.
   - Focus on getting the agent to produce meaningful insights about the tasks.

**Phase 5: Error Handling and Robustness (Estimated Time: 1 hour)**

1. **Add Error Handling:**

   - Wrap the agent processing within a `try...except` block to catch any exceptions raised by the agent.
   - Log the errors and decide on an appropriate course of action (e.g., skip the task, retry, or halt the process).

2. **Improve State Management:**
   - Ensure that the `SoMinEStateManager` is correctly handling transitions between phases.
   - Consider adding more robust validation of state transitions to prevent unexpected behavior.

**Phase 6: Testing (Estimated Time: 1 hour)**

1. **Write Unit Tests:**

   - Create unit tests for your custom processors (if any) and for the modified `TodoistIngestion` class.
   - Focus on testing the integration between `TodoistIngestion` and the agent components.
   - Use mocking to isolate components during testing.

2. **Run Tests:**
   - Use `poetry run test` to execute your tests and ensure they pass.

**Deliverables for Today:**

- **Integrated Agent:** The `SoMinEAgent` should be integrated into the `TodoistIngestion` pipeline and processing each task.
- **Basic Agent Output:** The agent should be producing some output (questions, instructions, reflections) for each task, even if it's not yet perfect.
- **Logging:** Logs should clearly show the agent's processing steps and any errors encountered.
- **Initial Error Handling:** Basic error handling should be in place to prevent agent exceptions from crashing the entire ingestion process.
- **Unit Tests (if time permits):** At least some basic unit tests should be written to cover the new code.

**Important Considerations:**

- **Asynchronous Operations:** The agent framework uses `async` and `await`. Make sure your `process_tasks` method is also `async` to avoid blocking.
- **Timeboxing:** Be strict with the time allocated to each phase. If you get stuck on a particular issue, consider moving on and coming back to it later. The goal is to get a basic working integration today, not a perfect one.
- **Iterative Improvement:** This is an iterative process. Don't expect to get everything right on the first try. Focus on getting a basic integration working, and then gradually improve it over time.

This plan should provide a solid foundation for integrating the SoMinE agent into your Todoist ingestion pipeline today. Remember to focus on the core functionality first and then gradually add refinements and improvements. Good luck!
