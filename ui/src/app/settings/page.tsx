"use client";

import {
  Box,
  Text,
  SimpleGrid,
  List,
  ListItem,
  ListIcon,
  Divider,
  Icon,
} from "@chakra-ui/react";
import { Card, CardHeader, CardBody } from "@chakra-ui/card";
import { FiShield, FiCheck } from "react-icons/fi";
import DashboardLayout from "@/components/DashboardLayout";
import { useStore } from "@/store";

export default function SettingsPage() {
  const { permissions } = useStore();

  const permissionGroups = {
    Users: permissions.filter(
      (p: string) => p.startsWith("VIEW_USERS") || p.startsWith("MANAGE_USERS")
    ),
    Roles: permissions.filter(
      (p: string) => p.startsWith("VIEW_ROLES") || p.startsWith("MANAGE_ROLES")
    ),
    Settings: permissions.filter(
      (p: string) =>
        p.startsWith("VIEW_SETTINGS") || p.startsWith("MANAGE_SETTINGS")
    ),
  };

  return (
    <DashboardLayout>
      <Box layerStyle="pageContainer">
        <Text fontSize="2xl" fontWeight="bold" mb={6} color="text.primary">
          System Settings
        </Text>

        <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
          {Object.entries(permissionGroups).map(([group, perms]) => (
            <Card key={group}>
              <CardHeader pb={0}>
                <Text fontSize="lg" fontWeight="semibold" color="text.primary">
                  <Icon as={FiShield} mr={2} color="brand.500" />
                  {group} Permissions
                </Text>
              </CardHeader>
              <CardBody>
                <List spacing={3}>
                  {perms.map((permission) => (
                    <ListItem
                      key={permission}
                      display="flex"
                      alignItems="center"
                    >
                      <ListIcon as={FiCheck} color="green.500" />
                      <Text color="text.secondary" fontSize="sm">
                        {permission.split("_").join(" ").toLowerCase()}
                      </Text>
                    </ListItem>
                  ))}
                </List>
              </CardBody>
            </Card>
          ))}
        </SimpleGrid>

        <Divider my={8} borderColor="border.subtle" />

        <Card>
          <CardHeader>
            <Text fontSize="lg" fontWeight="semibold" color="text.primary">
              About Permissions
            </Text>
          </CardHeader>
          <CardBody>
            <Text color="text.secondary">
              Permissions in this system are predefined and cannot be modified.
              They are assigned to roles, which can then be assigned to users.
              This ensures a consistent and secure access control system.
            </Text>
          </CardBody>
        </Card>
      </Box>
    </DashboardLayout>
  );
}
