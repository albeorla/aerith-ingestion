'use client'

import { Box, Container, Flex, Text } from '@chakra-ui/react'
import { ChatWindow } from '@/components/ChatWindow'

export default function ChatPage() {
  return (
    <Container maxW="container.xl" py={8}>
      <Flex direction="column" h="calc(100vh - 150px)">
        <Box mb={4}>
          <Text fontSize="2xl" fontWeight="bold">AI Chat</Text>
          <Text color="gray.600">Chat with your AI assistant about your data and documents.</Text>
        </Box>
        <Box flex={1} borderRadius="lg" overflow="hidden">
          <ChatWindow />
        </Box>
      </Flex>
    </Container>
  )
}
