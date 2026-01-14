# n8n Integration Setup Guide

## What You Need to Do

### 1. Get Your n8n Webhook URL

After setting up your n8n workflow with the Webhook node:

1. Open your n8n workflow
2. Click on the **Webhook node**
3. Look for the **Webhook URL** (it will look like: `https://your-n8n-instance.com/webhook/django-chatbot`)
4. **Copy this URL**

### 2. Configure Django Backend

Open `org/views.py` and find line ~310 where it says:

```python
N8N_WEBHOOK_URL = 'https://your-n8n-instance.com/webhook/django-chatbot'
```

**Replace this with your actual n8n webhook URL.**

### 3. (Optional) Add API Key Authentication

If you set up Header Auth in n8n:

1. Uncomment these lines in `org/views.py`:

```python
N8N_API_KEY = 'your-api-key-here'  # Add your actual key

# In the headers section:
'X-API-KEY': N8N_API_KEY,
```

## n8n Workflow Configuration Checklist

### ✅ Webhook Node
- **HTTP Method**: POST
- **Path**: django-chatbot (or your custom name)
- **Authentication**: None (or Header Auth with X-API-KEY)
- **Response Mode**: "When Last Node Finishes"

### ✅ AI Agent Node
- **Agent Type**: Conversational Agent
- **User Message**: `{{ $json.body.message }}`
- **Memory**: Connect Window Buffer Memory node
- **Model**: Connect OpenAI/Anthropic/Google model node with API key

### ✅ Respond to Webhook Node
- **Respond With**: JSON
- **Response Body**: 
  ```json
  {
    "reply": "{{ $json.output }}"
  }
  ```
- **HTTP Status Code**: 200

## Additional Context Available to n8n

Your Django backend sends this data to n8n:

```json
{
  "message": "User's question",
  "organization_id": 123,
  "organization_name": "Organization Name"
}
```

You can use these in your n8n workflow:
- `{{ $json.body.message }}` - The user's message
- `{{ $json.body.organization_id }}` - Organization ID
- `{{ $json.body.organization_name }}` - Organization name

## Testing the Connection

1. Make sure your Django server is running
2. Make sure your n8n workflow is **activated** (not just saved)
3. Go to the Insights tab in your dashboard
4. Type a message and press Send
5. Check the browser console (F12) for any errors
6. Check your n8n workflow execution logs

## Troubleshooting

### Error: "Failed to connect to AI service"
- Check that n8n workflow is activated
- Verify the webhook URL is correct
- Check n8n execution logs for errors

### Error: "Request timed out"
- n8n might be taking too long to respond
- Check if your AI model is responding
- Increase timeout in `views.py` if needed (currently 30 seconds)

### No response from bot
- Make sure the n8n response format is: `{"reply": "message"}`
- Check that "Respond to Webhook" node is connected
- Verify Response Mode is set to "When Last Node Finishes"

## Current Status

- ✅ Frontend chatbot UI created
- ✅ Django backend endpoint created (`/org/api/chat/`)
- ✅ Request forwarding to n8n configured
- ⏳ **TODO**: Add your n8n webhook URL
- ⏳ **TODO**: Activate n8n workflow
