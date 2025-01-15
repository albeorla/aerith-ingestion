"use client";

import {
  Box,
  Button,
  Flex,
  Input,
  InputGroup,
  InputLeftElement,
  Menu,
  MenuButton,
  MenuItem,
  MenuList,
  Table,
  Tbody,
  Td,
  Text,
  Th,
  Thead,
  Tr,
  IconButton,
  Badge,
  Wrap,
  WrapItem,
  useDisclosure,
  useToast,
} from "@chakra-ui/react";
import { Card } from "@chakra-ui/card";
import {
  FiSearch,
  FiPlus,
  FiMoreVertical,
  FiEdit2,
  FiTrash2,
} from "react-icons/fi";
import DashboardLayout from "@/components/DashboardLayout";
import RoleForm from "@/components/RoleForm";
import { Role, useStore } from "@/store";
import { useState } from "react";

export default function RolesPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedRole, setSelectedRole] = useState<Role | undefined>();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();

  const { roles, createRole, updateRole, deleteRole } = useStore();

  const filteredRoles = roles.filter((role) =>
    role.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleAddRole = () => {
    setSelectedRole(undefined);
    onOpen();
  };

  const handleEditRole = (role: Role) => {
    setSelectedRole(role);
    onOpen();
  };

  const handleDeleteRole = (role: Role) => {
    try {
      deleteRole(role.id);
      toast({
        title: "Role deleted",
        description: `${role.name} has been removed`,
        status: "success",
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to delete role",
        status: "error",
        duration: 3000,
      });
    }
  };

  const handleSubmit = (roleData: Omit<Role, "id">) => {
    try {
      if (selectedRole) {
        updateRole(selectedRole.id, roleData);
        toast({
          title: "Role updated",
          description: `${roleData.name} has been updated`,
          status: "success",
          duration: 3000,
        });
      } else {
        createRole(roleData);
        toast({
          title: "Role created",
          description: `${roleData.name} has been added`,
          status: "success",
          duration: 3000,
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to save role",
        status: "error",
        duration: 3000,
      });
    }
  };

  return (
    <DashboardLayout>
      <Box layerStyle="pageContainer">
        <Flex justify="space-between" align="center" mb={6}>
          <Text fontSize="2xl" fontWeight="bold" color="text.primary">
            Roles Management
          </Text>
          <Button
            leftIcon={<FiPlus />}
            colorScheme="brand"
            onClick={handleAddRole}
          >
            Add Role
          </Button>
        </Flex>

        <Card mb={6}>
          <Flex p={4} gap={4} wrap="wrap">
            <InputGroup maxW={{ base: "full", md: "320px" }}>
              <InputLeftElement pointerEvents="none">
                <FiSearch color="gray.300" />
              </InputLeftElement>
              <Input
                placeholder="Search roles..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </InputGroup>
          </Flex>
        </Card>

        <Card>
          <Box overflowX="auto">
            <Table>
              <Thead>
                <Tr>
                  <Th>Name</Th>
                  <Th>Permissions</Th>
                  <Th width="1"></Th>
                </Tr>
              </Thead>
              <Tbody>
                {filteredRoles.map((role) => (
                  <Tr key={role.id}>
                    <Td fontWeight="medium">
                      <Badge
                        colorScheme={role.name === "admin" ? "purple" : "blue"}
                      >
                        {role.name}
                      </Badge>
                    </Td>
                    <Td>
                      <Wrap spacing={2}>
                        {role.permissions.map((permission) => (
                          <WrapItem key={permission}>
                            <Badge colorScheme="green" variant="subtle">
                              {permission}
                            </Badge>
                          </WrapItem>
                        ))}
                      </Wrap>
                    </Td>
                    <Td>
                      <Menu>
                        <MenuButton
                          as={IconButton}
                          variant="ghost"
                          size="sm"
                          aria-label="More options"
                          icon={<FiMoreVertical />}
                        />
                        <MenuList>
                          <MenuItem
                            icon={<FiEdit2 />}
                            onClick={() => handleEditRole(role)}
                          >
                            Edit
                          </MenuItem>
                          <MenuItem
                            icon={<FiTrash2 />}
                            color="red.500"
                            onClick={() => handleDeleteRole(role)}
                          >
                            Delete
                          </MenuItem>
                        </MenuList>
                      </Menu>
                    </Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </Box>
        </Card>
      </Box>

      <RoleForm
        isOpen={isOpen}
        onClose={onClose}
        role={selectedRole}
        onSubmit={handleSubmit}
      />
    </DashboardLayout>
  );
}
