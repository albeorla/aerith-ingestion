"use client";

import {
  Box,
  Flex,
  Icon,
  Text,
  Link,
  BoxProps,
  IconButton,
  useDisclosure,
  useColorMode,
} from "@chakra-ui/react";
import {
  FiHome,
  FiUsers,
  FiSettings,
  FiShield,
  FiMenu,
  FiX,
  FiSun,
  FiMoon,
  FiMessageSquare,
} from "react-icons/fi";
import { IconType } from "react-icons";
import NextLink from "next/link";
import { usePathname } from "next/navigation";

interface LinkItemProps {
  name: string;
  icon: IconType;
  href: string;
}

const LinkItems: Array<LinkItemProps> = [
  { name: "Dashboard", icon: FiHome, href: "/dashboard" },
  { name: "Chat", icon: FiMessageSquare, href: "/chat" },
  { name: "Users", icon: FiUsers, href: "/users" },
  { name: "Roles", icon: FiShield, href: "/roles" },
  { name: "Settings", icon: FiSettings, href: "/settings" },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { colorMode, toggleColorMode } = useColorMode();

  return (
    <Box minH="100vh" bg="bg.canvas">
      <SidebarContent
        onClose={onClose}
        display={{ base: isOpen ? "block" : "none", md: "block" }}
      />

      <Box transition="all 0.2s" ml={{ base: 0, md: 60 }} p="4">
        <Flex
          as="header"
          align="center"
          justify="space-between"
          w="full"
          px="4"
          bg="bg.surface"
          borderBottomWidth="1px"
          borderColor="border.subtle"
          h="14"
          display={{ base: "flex", md: "none" }}
          position="fixed"
          top="0"
          zIndex="sticky"
          left="0"
          right="0"
        >
          <IconButton
            onClick={onOpen}
            variant="ghost"
            aria-label="open menu"
            icon={<FiMenu />}
          />
          <Text fontSize="2xl" fontWeight="bold">
            RBAC
          </Text>
          <IconButton
            variant="ghost"
            aria-label="Toggle color mode"
            icon={colorMode === "light" ? <FiMoon /> : <FiSun />}
            onClick={toggleColorMode}
          />
        </Flex>
        <Box pt={{ base: "14", md: "0" }}>{children}</Box>
      </Box>
    </Box>
  );
}

interface SidebarProps extends BoxProps {
  onClose: () => void;
}

const SidebarContent = ({ onClose, ...rest }: SidebarProps) => {
  const pathname = usePathname();
  const { colorMode, toggleColorMode } = useColorMode();

  return (
    <Box
      bg="bg.surface"
      borderRightWidth="1px"
      borderColor="border.subtle"
      w={{ base: "full", md: 60 }}
      pos="fixed"
      h="full"
      {...rest}
    >
      <Flex h="20" alignItems="center" mx="8" justifyContent="space-between">
        <Text fontSize="2xl" fontWeight="bold">
          RBAC
        </Text>
        <Flex gap={2}>
          <IconButton
            variant="ghost"
            aria-label="Toggle color mode"
            icon={colorMode === "light" ? <FiMoon /> : <FiSun />}
            onClick={toggleColorMode}
          />
          <IconButton
            display={{ base: "flex", md: "none" }}
            onClick={onClose}
            variant="ghost"
            aria-label="close menu"
            icon={<FiX />}
          />
        </Flex>
      </Flex>
      {LinkItems.map((link) => (
        <NavItem
          key={link.name}
          icon={link.icon}
          href={link.href}
          isActive={pathname === link.href}
        >
          {link.name}
        </NavItem>
      ))}
    </Box>
  );
};

interface NavItemProps {
  icon: IconType;
  children: React.ReactNode;
  href: string;
  isActive?: boolean;
}

const NavItem = ({ icon, children, href, isActive, ...rest }: NavItemProps) => {
  return (
    <Link
      as={NextLink}
      href={href}
      style={{ textDecoration: "none" }}
      _focus={{ boxShadow: "none" }}
    >
      <Flex
        align="center"
        p="4"
        mx="4"
        borderRadius="lg"
        role="group"
        cursor="pointer"
        bg={isActive ? "brand.500" : "transparent"}
        color={isActive ? "white" : "text.primary"}
        _hover={{
          bg: isActive ? "brand.600" : "bg.subtle",
          color: isActive ? "white" : "text.primary",
        }}
        {...rest}
      >
        {icon && (
          <Icon
            mr="4"
            fontSize="16"
            as={icon}
            color={isActive ? "white" : "text.secondary"}
            _groupHover={{
              color: isActive ? "white" : "text.primary",
            }}
          />
        )}
        {children}
      </Flex>
    </Link>
  );
};
