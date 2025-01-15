"use client";

import {
  Box,
  SimpleGrid,
  Text,
  Card,
  CardBody,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Flex,
  Icon,
  Stack,
  Heading,
  Divider,
} from "@chakra-ui/react";
import DashboardLayout from "@/components/DashboardLayout";
import { useStore } from "@/store";
import { useEffect, useState } from "react";
import { FiUserPlus, FiShield, FiSettings } from "react-icons/fi";
import { useRouter } from "next/navigation";

export default function Home() {
  const { users, roles } = useStore();
  const [mounted, setMounted] = useState(false);
  const router = useRouter();

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return null;
  }

  const activeUsers = users.filter((user) => user.isActive);
  const adminUsers = users.filter((user) => user.role === "admin");

  return (
    <DashboardLayout>
      <Box layerStyle="pageContainer">
        <Stack spacing={8}>
          {/* Welcome Section */}
          <Box>
            <Heading size="lg" mb={2}>
              Welcome to RBAC Dashboard
            </Heading>
            <Text color="text.secondary">
              Manage your users, roles, and permissions from one central
              location.
            </Text>
          </Box>

          {/* Stats Overview */}
          <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>Total Users</StatLabel>
                  <StatNumber>{users.length}</StatNumber>
                  <StatHelpText>{activeUsers.length} active</StatHelpText>
                </Stat>
              </CardBody>
            </Card>

            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>Total Roles</StatLabel>
                  <StatNumber>{roles.length}</StatNumber>
                  <StatHelpText>Defined permissions</StatHelpText>
                </Stat>
              </CardBody>
            </Card>

            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>Active Users</StatLabel>
                  <StatNumber>{activeUsers.length}</StatNumber>
                  <StatHelpText>
                    {((activeUsers.length / users.length) * 100).toFixed(1)}% of
                    total
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>

            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>Admin Users</StatLabel>
                  <StatNumber>{adminUsers.length}</StatNumber>
                  <StatHelpText>With full access</StatHelpText>
                </Stat>
              </CardBody>
            </Card>
          </SimpleGrid>

          <Divider />

          {/* Quick Actions */}
          <Box>
            <Text fontSize="xl" fontWeight="medium" mb={4}>
              Quick Actions
            </Text>
            <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6}>
              <Card
                role="group"
                cursor="pointer"
                onClick={() => router.push("/users")}
                _hover={{ transform: "translateY(-2px)", shadow: "md" }}
                transition="all 0.2s"
              >
                <CardBody>
                  <Flex align="center" gap={3}>
                    <Icon as={FiUserPlus} boxSize={5} color="brand.500" />
                    <Box>
                      <Text fontWeight="medium">Manage Users</Text>
                      <Text fontSize="sm" color="text.secondary">
                        Add, edit, or remove users
                      </Text>
                    </Box>
                  </Flex>
                </CardBody>
              </Card>

              <Card
                role="group"
                cursor="pointer"
                onClick={() => router.push("/roles")}
                _hover={{ transform: "translateY(-2px)", shadow: "md" }}
                transition="all 0.2s"
              >
                <CardBody>
                  <Flex align="center" gap={3}>
                    <Icon as={FiShield} boxSize={5} color="brand.500" />
                    <Box>
                      <Text fontWeight="medium">Manage Roles</Text>
                      <Text fontSize="sm" color="text.secondary">
                        Configure roles and permissions
                      </Text>
                    </Box>
                  </Flex>
                </CardBody>
              </Card>

              <Card
                role="group"
                cursor="pointer"
                onClick={() => router.push("/settings")}
                _hover={{ transform: "translateY(-2px)", shadow: "md" }}
                transition="all 0.2s"
              >
                <CardBody>
                  <Flex align="center" gap={3}>
                    <Icon as={FiSettings} boxSize={5} color="brand.500" />
                    <Box>
                      <Text fontWeight="medium">Settings</Text>
                      <Text fontSize="sm" color="text.secondary">
                        Configure system settings
                      </Text>
                    </Box>
                  </Flex>
                </CardBody>
              </Card>
            </SimpleGrid>
          </Box>

          {/* System Status */}
          <Card>
            <CardBody>
              <Text fontSize="lg" fontWeight="medium" mb={4}>
                System Status
              </Text>
              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                <Box>
                  <Text color="text.secondary" fontSize="sm">
                    Version
                  </Text>
                  <Text fontWeight="medium">1.0.0-beta</Text>
                </Box>
                <Box>
                  <Text color="text.secondary" fontSize="sm">
                    Last Updated
                  </Text>
                  <Text fontWeight="medium">
                    {new Date().toLocaleDateString()}
                  </Text>
                </Box>
              </SimpleGrid>
            </CardBody>
          </Card>
        </Stack>
      </Box>
    </DashboardLayout>
  );
}
