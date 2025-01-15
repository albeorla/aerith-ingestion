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
  Select,
  Table,
  Tbody,
  Td,
  Text,
  Th,
  Thead,
  Tr,
  useDisclosure,
  Badge,
  IconButton,
  useToast,
  AlertDialog,
  AlertDialogBody,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogContent,
  AlertDialogOverlay,
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
import UserForm from "@/components/UserForm";
import { User, useStore } from "@/store";
import { useState } from "react";
import React from "react";
import { FocusableElement } from "@chakra-ui/utils";

export default function UsersPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [roleFilter, setRoleFilter] = useState("all");
  const [selectedUser, setSelectedUser] = useState<User | undefined>();
  const [userToDelete, setUserToDelete] = useState<User | null>(null);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const {
    isOpen: isAlertOpen,
    onOpen: onAlertOpen,
    onClose: onAlertClose,
  } = useDisclosure();
  const toast = useToast();
  const cancelRef = React.useRef<HTMLButtonElement>(null);

  const { users, roles, createUser, updateUser, deleteUser } = useStore();

  const filteredUsers = users.filter((user) => {
    const matchesSearch =
      user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      user.email.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesRole = roleFilter === "all" || user.role === roleFilter;
    return matchesSearch && matchesRole;
  });

  const handleAddUser = () => {
    setSelectedUser(undefined);
    onOpen();
  };

  const handleEditUser = (user: User) => {
    setSelectedUser(user);
    onOpen();
  };

  const handleDeleteClick = (user: User) => {
    setUserToDelete(user);
    onAlertOpen();
  };

  const handleDeleteUser = () => {
    if (userToDelete) {
      try {
        deleteUser(userToDelete.id);
        toast({
          title: "User deleted",
          description: `${userToDelete.name} has been removed`,
          status: "success",
          duration: 3000,
        });
      } catch (error) {
        toast({
          title: "Error",
          description:
            error instanceof Error ? error.message : "Failed to delete user",
          status: "error",
          duration: 3000,
        });
      }
      setUserToDelete(null);
    }
    onAlertClose();
  };

  const handleSubmit = (userData: Omit<User, "id">) => {
    try {
      if (selectedUser) {
        updateUser(selectedUser.id, userData);
        toast({
          title: "User updated",
          description: `${userData.name} has been updated`,
          status: "success",
          duration: 3000,
        });
      } else {
        createUser(userData);
        toast({
          title: "User created",
          description: `${userData.name} has been added`,
          status: "success",
          duration: 3000,
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description:
          error instanceof Error ? error.message : "Failed to save user",
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
            Users Management
          </Text>
          <Button
            leftIcon={<FiPlus />}
            colorScheme="brand"
            onClick={handleAddUser}
          >
            Add User
          </Button>
        </Flex>

        <Card mb={6}>
          <Flex p={4} gap={4} wrap="wrap">
            <InputGroup maxW={{ base: "full", md: "320px" }}>
              <InputLeftElement pointerEvents="none">
                <FiSearch color="gray.300" />
              </InputLeftElement>
              <Input
                placeholder="Search users..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </InputGroup>
            <Select
              maxW={{ base: "full", md: "200px" }}
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
            >
              <option value="all">All Roles</option>
              {roles.map((role) => (
                <option key={role.name} value={role.name}>
                  {role.name}
                </option>
              ))}
            </Select>
          </Flex>
        </Card>

        <Card>
          <Box overflowX="auto">
            <Table>
              <Thead>
                <Tr>
                  <Th>Name</Th>
                  <Th>Email</Th>
                  <Th>Role</Th>
                  <Th>Status</Th>
                  <Th width="1"></Th>
                </Tr>
              </Thead>
              <Tbody>
                {filteredUsers.map((user) => (
                  <Tr key={user.id}>
                    <Td fontWeight="medium">{user.name}</Td>
                    <Td>{user.email}</Td>
                    <Td>
                      <Badge
                        colorScheme={user.role === "admin" ? "purple" : "blue"}
                      >
                        {user.role}
                      </Badge>
                    </Td>
                    <Td>
                      <Badge colorScheme={user.isActive ? "green" : "gray"}>
                        {user.isActive ? "Active" : "Inactive"}
                      </Badge>
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
                            onClick={() => handleEditUser(user)}
                          >
                            Edit
                          </MenuItem>
                          <MenuItem
                            icon={<FiTrash2 />}
                            color="red.500"
                            onClick={() => handleDeleteClick(user)}
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

      <UserForm
        isOpen={isOpen}
        onClose={onClose}
        user={selectedUser}
        onSubmit={handleSubmit}
      />

      <AlertDialog
        isOpen={isAlertOpen}
        onClose={onAlertClose}
        leastDestructiveRef={cancelRef as React.RefObject<FocusableElement>}
      >
        <AlertDialogOverlay>
          <AlertDialogContent>
            <AlertDialogHeader fontSize="lg" fontWeight="bold">
              Delete User
            </AlertDialogHeader>

            <AlertDialogBody>
              Are you sure you want to delete {userToDelete?.name}? This action
              cannot be undone.
            </AlertDialogBody>

            <AlertDialogFooter>
              <Button ref={cancelRef} onClick={onAlertClose}>
                Cancel
              </Button>
              <Button colorScheme="red" onClick={handleDeleteUser} ml={3}>
                Yes, Delete
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>
    </DashboardLayout>
  );
}
