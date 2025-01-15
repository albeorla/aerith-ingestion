import { Message, StreamingTextResponse } from 'ai'

export const runtime = 'edge'

const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:8000'

async function fetchTaskData(query: string) {
  try {
    console.log('Sending search request:', { query, url: `${BACKEND_URL}/api/tasks/search` })
    
    const response = await fetch(`${BACKEND_URL}/api/tasks/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query })
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error('Backend error response:', errorText)
      throw new Error(`Backend error: ${response.status} ${response.statusText}`)
    }

    const data = await response.json()
    console.log('Received task data:', data)
    return data
  } catch (error) {
    console.error('Error fetching from backend:', error)
    throw new Error('Failed to connect to backend service. Is it running?')
  }
}

interface Task {
  id: string
  content: string
  project?: string
  due_date?: string
  priority?: number
}

function formatPriority(priority?: number): string {
  if (!priority) return ''
  const priorities = ['', '🔴 High', '🟡 Medium', '🟢 Low']
  return priorities[priority] || ''
}

function formatDate(dateStr?: string): string {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString(undefined, { 
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    })
  } catch {
    return ''
  }
}

function formatTask(task: Task): string {
  const parts = []
  
  // Format task content
  parts.push(task.content)
  
  // Additional info in a group
  const metadata = []
  if (task.project) {
    metadata.push(`📁 ${task.project}`)
  }
  
  const priority = formatPriority(task.priority)
  if (priority) {
    metadata.push(priority)
  }
  
  const dueDate = formatDate(task.due_date)
  if (dueDate) {
    metadata.push(`📅 ${dueDate}`)
  }

  // Join all parts with spacing
  return `${parts[0]} ${metadata.join(' • ')}`
}

function formatResponse(tasks: Task[]): string {
  if (tasks.length === 0) return "No tasks found."
  
  const header = "Here are the tasks I found:\n"
  const taskGroups: string[] = []
  
  // Group tasks by project
  const projectGroups = new Map<string, Task[]>()
  tasks.forEach(task => {
    const project = task.project || 'No Project'
    if (!projectGroups.has(project)) {
      projectGroups.set(project, [])
    }
    projectGroups.get(project)!.push(task)
  })
  
  // Format each project group
  for (const [project, projectTasks] of projectGroups) {
    if (project !== 'No Project') {
      taskGroups.push(`\n📁 ${project}:`)
    }
    projectTasks.forEach((task, i) => {
      const number = tasks.indexOf(task) + 1
      taskGroups.push(`${number}. ${formatTask(task)}`)
    })
  }
  
  return header + taskGroups.join('\n')
}

export async function POST(req: Request) {
  try {
    const { messages }: { messages: Message[] } = await req.json()
    console.log('Received chat request with messages:', messages)
    
    // Validate request
    if (!messages || !Array.isArray(messages) || messages.length === 0) {
      return new Response('Missing or invalid messages', { status: 400 })
    }

    const lastMessage = messages[messages.length - 1]
    if (!lastMessage.content || typeof lastMessage.content !== 'string') {
      return new Response('Invalid message content', { status: 400 })
    }

    // Get task data from Python backend
    const taskData = await fetchTaskData(lastMessage.content)
    const response = formatResponse(taskData)
    console.log('Final formatted response:', response)

    // Create a stream with just the text content
    const stream = new ReadableStream({
      async start(controller) {
        const encoder = new TextEncoder()
        controller.enqueue(encoder.encode(response))
        controller.close()
      }
    })

    return new StreamingTextResponse(stream)
  } catch (error) {
    console.error('Error in chat API:', error)
    return new Response(error instanceof Error ? error.message : 'Internal Server Error', { 
      status: 500,
      headers: {
        'Content-Type': 'application/json'
      }
    })
  }
} 