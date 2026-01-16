# n8n Workflow Configuration for Context Support

## Overview
The chat interface now sends context data (selected events and students) along with each message to your n8n webhook. This allows your AI to provide more accurate, context-aware responses.

## Data Structure Sent to n8n

When a user sends a message with context selected, the payload sent to your n8n webhook will include:

```json
{
  "message": "User's message text",
  "sessionId": "uuid-session-id",
  "organization_id": 1,
  "organization_name": "Organization Name",
  "user_id": 1,
  "conversation_history": [
    {
      "role": "user",
      "content": "Previous user message"
    },
    {
      "role": "assistant",
      "content": "Previous bot response"
    }
  ],
  "context": {
    "events": [
      {
        "id": 1,
        "title": "Event Title",
        "description": "Event description",
        "date": "2026-01-12",
        "start_time": "08:00:00",
        "end_time": "17:00:00",
        "is_active": true,
        "total_attendees": 45
      }
    ],
    "students": [
      {
        "id": 1,
        "student_id": "STU001",
        "first_name": "John",
        "last_name": "Doe",
        "middle_name": "",
        "email": "john.doe@example.com",
        "course": "Computer Science",
        "year_level": 2
      }
    ]
  }
}
```

## n8n Workflow Configuration

### Step 1: Access the Context Data

In your n8n workflow, after the Webhook node receives the data, you can access the context using expressions:

**To get selected events:**
```
{{ $json.context.events }}
```

**To get selected students:**
```
{{ $json.context.students }}
```

**To check if context exists:**
```
{{ $json.context.events.length > 0 || $json.context.students.length > 0 }}
```

### Step 2: Format Context for AI

You'll want to format the context data into a readable string that you can include in your AI prompt. Here's an example using an n8n Function node:

```javascript
// Format context for AI prompt
const context = $input.item.json.context;
let contextText = "";

if (context.events && context.events.length > 0) {
  contextText += "## Selected Events:\n\n";
  context.events.forEach((event, index) => {
    const date = new Date(event.date).toLocaleDateString();
    contextText += `${index + 1}. **${event.title}**\n`;
    contextText += `   - Date: ${date}\n`;
    contextText += `   - Time: ${event.start_time} - ${event.end_time}\n`;
    contextText += `   - Attendees: ${event.total_attendees}\n`;
    if (event.description) {
      contextText += `   - Description: ${event.description}\n`;
    }
    contextText += "\n";
  });
}

if (context.students && context.students.length > 0) {
  contextText += "## Selected Students:\n\n";
  context.students.forEach((student, index) => {
    contextText += `${index + 1}. **${student.first_name} ${student.last_name}**\n`;
    contextText += `   - Student ID: ${student.student_id}\n`;
    contextText += `   - Course: ${student.course}\n`;
    contextText += `   - Year Level: ${student.year_level}\n`;
    contextText += `   - Email: ${student.email}\n`;
    contextText += "\n";
  });
}

return {
  json: {
    ...$input.item.json,
    formatted_context: contextText,
    has_context: contextText.length > 0
  }
};
```

### Step 3: Update Your AI Prompt

Modify your AI prompt (in OpenAI/ChatGPT node or similar) to include the context:

**Option A: Add to System Prompt**
```
You are an AI assistant for an attendance monitoring system.

[Your existing system prompt here]

When the user provides context about specific events or students, use that information to provide more accurate answers. The context will be provided in the message.
```

**Option B: Add to User Message**
In your AI node, construct the user message like this:

```
{{ $json.message }}

{{ $json.formatted_context }}
```

**Option C: Combined Approach (Recommended)**
Use a Function node to combine everything:

```javascript
const message = $input.item.json.message;
const context = $input.item.json.formatted_context;
const conversationHistory = $input.item.json.conversation_history;

// Build the enhanced message
let enhancedMessage = message;
if (context) {
  enhancedMessage += "\n\n" + context;
}

// Prepare messages array for OpenAI/ChatGPT
const messages = [];

// Add system message with context awareness
messages.push({
  role: "system",
  content: "You are an AI assistant for an attendance monitoring system. When users reference specific events or students in their context, use that information to provide accurate, detailed responses."
});

// Add conversation history
conversationHistory.forEach(msg => {
  messages.push({
    role: msg.role,
    content: msg.content
  });
});

// Add current message with context
messages.push({
  role: "user",
  content: enhancedMessage
});

return {
  json: {
    messages: messages,
    original_message: message,
    has_context: context ? context.length > 0 : false
  }
};
```

### Step 4: Example n8n Workflow Structure

```
1. Webhook Node
   ↓
2. Function Node (Format Context)
   - Extract and format context data
   - Prepare enhanced message
   ↓
3. OpenAI/ChatGPT Node
   - Use formatted messages array
   - Include context in prompts
   ↓
4. Function Node (Format Response)
   - Extract AI response
   - Format as needed
   ↓
5. Return Response
   - Send back to webhook
```

## Example n8n Expressions

### Check if events are selected:
```
{{ $json.context && $json.context.events && $json.context.events.length > 0 }}
```

### Get first selected event title:
```
{{ $json.context.events[0].title }}
```

### Get all selected student names:
```
{{ $json.context.students.map(s => s.first_name + ' ' + s.last_name).join(', ') }}
```

### Count total context items:
```
{{ ($json.context.events ? $json.context.events.length : 0) + ($json.context.students ? $json.context.students.length : 0) }}
```

## Handling Empty Context

If no context is selected, the `context` object will still be present but with empty arrays:

```json
{
  "context": {
    "events": [],
    "students": []
  }
}
```

Always check for length before accessing context items:

```
{{ $json.context.events && $json.context.events.length > 0 ? $json.context.events[0].title : "No events selected" }}
```

## Best Practices

1. **Always check for context** - Don't assume context is always present
2. **Format context clearly** - Make it easy for the AI to understand
3. **Include in prompts** - Add context to both system and user messages for best results
4. **Preserve conversation history** - The `conversation_history` array helps maintain context across messages
5. **Use structured data** - The context is already structured JSON, making it easy to parse

## Testing

1. Test with no context selected - ensure workflow handles empty arrays
2. Test with only events selected
3. Test with only students selected  
4. Test with both events and students selected
5. Test with multiple items in each category

## Troubleshooting

**Context not appearing in n8n:**
- Check that the context selector UI is working
- Verify the payload in n8n's webhook execution logs
- Ensure you're accessing `$json.context` correctly

**AI not using context:**
- Verify context is included in the AI prompt/messages
- Check that context is formatted in a readable way
- Ensure the system prompt mentions using context data

**Context arrays are empty:**
- This is normal when no context is selected
- Always check array length before accessing items
