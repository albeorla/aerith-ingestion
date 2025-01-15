'use client'

import { Box, Text } from '@chakra-ui/react'
import { ChatWindow } from '@/components/ChatWindow'
import DashboardLayout from '@/components/DashboardLayout'

export default function ChatPage() {
  return (
    <DashboardLayout>
      <Box p={4}>
        <Box mb={4}>
          <Text fontSize="2xl" fontWeight="bold">AI Chat</Text>
          <Text color="gray.600">Chat with your AI assistant about your data and documents.</Text>
        </Box>
        <Box 
          flex={1} 
          borderRadius="lg" 
          overflow="hidden"
          h="calc(100vh - 200px)"
          bg="white"
          boxShadow="sm"
        >
          <ChatWindow />
        </Box>
      </Box>
    </DashboardLayout>
  )
}
