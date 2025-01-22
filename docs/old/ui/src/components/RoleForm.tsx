"use client";

import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Button,
  FormControl,
  FormLabel,
  Input,
  FormErrorMessage,
  VStack,
  Checkbox,
  SimpleGrid,
} from "@chakra-ui/react";
import { Role, Permission, useStore } from "@/store";
import { useState } from "react";

interface RoleFormProps {
  isOpen: boolean;
  onClose: () => void;
  role?: Role;
  onSubmit: (role: Omit<Role, "id">) => void;
}

export default function RoleForm({
  isOpen,
  onClose,
  role,
  onSubmit,
}: RoleFormProps) {
  const { permissions } = useStore();
  const [formData, setFormData] = useState<Omit<Role, "id">>({
    name: role?.name ?? "",
    permissions: role?.permissions ?? [],
  });
  const [errors, setErrors] = useState<Partial<Record<keyof Role, string>>>({});

  const validateForm = () => {
    const newErrors: Partial<Record<keyof Role, string>> = {};

    if (!formData.name.trim()) {
      newErrors.name = "Name is required";
    }

    if (formData.permissions.length === 0) {
      newErrors.permissions = "At least one permission is required";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (validateForm()) {
      onSubmit(formData);
      onClose();
    }
  };

  const togglePermission = (permission: Permission) => {
    setFormData((prev) => ({
      ...prev,
      permissions: prev.permissions.includes(permission)
        ? prev.permissions.filter((p) => p !== permission)
        : [...prev.permissions, permission],
    }));
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>{role ? "Edit Role" : "Add Role"}</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <VStack spacing={6}>
            <FormControl isInvalid={!!errors.name}>
              <FormLabel>Name</FormLabel>
              <Input
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                placeholder="Enter role name"
              />
              <FormErrorMessage>{errors.name}</FormErrorMessage>
            </FormControl>

            <FormControl isInvalid={!!errors.permissions}>
              <FormLabel>Permissions</FormLabel>
              <SimpleGrid columns={2} spacing={3}>
                {permissions.map((permission) => (
                  <Checkbox
                    key={permission}
                    isChecked={formData.permissions.includes(permission)}
                    onChange={() => togglePermission(permission)}
                  >
                    {permission.split("_").join(" ").toLowerCase()}
                  </Checkbox>
                ))}
              </SimpleGrid>
              <FormErrorMessage>{errors.permissions}</FormErrorMessage>
            </FormControl>
          </VStack>
        </ModalBody>

        <ModalFooter gap={2}>
          <Button variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button colorScheme="brand" onClick={handleSubmit}>
            {role ? "Save Changes" : "Add Role"}
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
}
