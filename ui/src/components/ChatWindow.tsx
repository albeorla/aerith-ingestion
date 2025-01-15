'use client'

import { useChat } from 'ai/react'
import { Box, Input, Button, VStack, HStack, Text, Spinner } from '@chakra-ui/react'
import { useEffect, useRef } from 'react'

export function ChatWindow() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const formatMessage = (content: string) => {
    return content.split('\n').map((line, i) => (
      <Text key={i} whiteSpace="pre-wrap" mb={1}>
        {line}
      </Text>
    ))
  }

  return (
    <Box h="100%" bg="gray.50" p={4}>
      <VStack h="100%" spacing={4}>
        <Box 
          flex={1} 
          w="100%" 
          overflowY="auto" 
          bg="white" 
          p={4} 
          borderRadius="md"
          boxShadow="sm"
        >
          {messages.map((message, i) => (
            <Box 
              key={i} 
              mb={4} 
              p={3} 
              borderRadius="lg"
              bg={message.role === 'assistant' ? 'blue.50' : 'gray.50'}
              alignSelf={message.role === 'assistant' ? 'flex-start' : 'flex-end'}
              maxW="100%"
              fontFamily="monospace"
            >
              {formatMessage(message.content)}
            </Box>
          ))}
          <div ref={messagesEndRef} />
        </Box>
        
        <form onSubmit={handleSubmit} style={{ width: '100%' }}>
          <HStack w="100%">
            <Input
              value={input}
              onChange={handleInputChange}
              placeholder="Type your message..."
              bg="white"
              disabled={isLoading}
            />
            <Button 
              type="submit" 
              colorScheme="blue"
              isLoading={isLoading}
              loadingText="Sending..."
            >
              Send
            </Button>
          </HStack>
        </form>
      </VStack>
    </Box>
  )
}
