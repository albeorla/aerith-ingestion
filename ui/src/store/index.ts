"use client";

import { useEffect, useState } from "react";

// Types
export interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  isActive: boolean;
}

export interface Role {
  id: string;
  name: string;
  permissions: Permission[];
}

export enum Permission {
  VIEW_USERS = "VIEW_USERS",
  MANAGE_USERS = "MANAGE_USERS",
  VIEW_ROLES = "VIEW_ROLES",
  MANAGE_ROLES = "MANAGE_ROLES",
  VIEW_SETTINGS = "VIEW_SETTINGS",
  MANAGE_SETTINGS = "MANAGE_SETTINGS",
}

// In-memory store
class Store {
  private static instance: Store;
  private subscribers: Set<() => void> = new Set();

  private users: User[] = [
    {
      id: "1",
      name: "Admin User",
      email: "admin@example.com",
      role: "admin",
      isActive: true,
    },
    {
      id: "2",
      name: "Regular User",
      email: "user@example.com",
      role: "user",
      isActive: true,
    },
  ];

  private roles: Role[] = [
    {
      id: "1",
      name: "admin",
      permissions: Object.values(Permission),
    },
    {
      id: "2",
      name: "user",
      permissions: [
        Permission.VIEW_USERS,
        Permission.VIEW_ROLES,
        Permission.VIEW_SETTINGS,
      ],
    },
  ];

  private constructor() {
    if (typeof window !== "undefined") {
      // Load from localStorage in client
      const savedUsers = localStorage.getItem("users");
      const savedRoles = localStorage.getItem("roles");

      if (savedUsers) this.users = JSON.parse(savedUsers);
      if (savedRoles) this.roles = JSON.parse(savedRoles);
    }
  }

  public static getInstance(): Store {
    if (!Store.instance) {
      Store.instance = new Store();
    }
    return Store.instance;
  }

  private notify() {
    if (typeof window !== "undefined") {
      localStorage.setItem("users", JSON.stringify(this.users));
      localStorage.setItem("roles", JSON.stringify(this.roles));
    }
    this.subscribers.forEach((callback) => callback());
  }

  public subscribe(callback: () => void) {
    this.subscribers.add(callback);
    return () => {
      this.subscribers.delete(callback);
    };
  }

  // User operations
  getUsers(): User[] {
    return this.users;
  }

  createUser(user: Omit<User, "id">): User {
    const newUser = { ...user, id: crypto.randomUUID() };
    this.users.push(newUser);
    this.notify();
    return newUser;
  }

  updateUser(id: string, updates: Partial<Omit<User, "id">>): User {
    const index = this.users.findIndex((u) => u.id === id);
    if (index === -1) throw new Error("User not found");

    this.users[index] = { ...this.users[index], ...updates };
    this.notify();
    return this.users[index];
  }

  deleteUser(id: string): void {
    const index = this.users.findIndex((u) => u.id === id);
    if (index === -1) throw new Error("User not found");

    this.users.splice(index, 1);
    this.notify();
  }

  // Role operations
  getRoles(): Role[] {
    return this.roles;
  }

  createRole(role: Omit<Role, "id">): Role {
    const newRole = { ...role, id: crypto.randomUUID() };
    this.roles.push(newRole);
    this.notify();
    return newRole;
  }

  updateRole(id: string, updates: Partial<Omit<Role, "id">>): Role {
    const index = this.roles.findIndex((r) => r.id === id);
    if (index === -1) throw new Error("Role not found");

    this.roles[index] = { ...this.roles[index], ...updates };
    this.notify();
    return this.roles[index];
  }

  deleteRole(id: string): void {
    const index = this.roles.findIndex((r) => r.id === id);
    if (index === -1) throw new Error("Role not found");

    // Don't allow deleting if users are using this role
    const usersWithRole = this.users.find(
      (u) => u.role === this.roles[index].name
    );
    if (usersWithRole) throw new Error("Cannot delete role that is in use");

    this.roles.splice(index, 1);
    this.notify();
  }

  getPermissions(): Permission[] {
    return Object.values(Permission);
  }
}

export const store = Store.getInstance();

// React hook for store state
export function useStore() {
  const [, setUpdate] = useState({});

  useEffect(() => {
    return store.subscribe(() => setUpdate({}));
  }, []);

  return {
    users: store.getUsers(),
    roles: store.getRoles(),
    permissions: store.getPermissions(),
    createUser: store.createUser.bind(store),
    updateUser: store.updateUser.bind(store),
    deleteUser: store.deleteUser.bind(store),
    createRole: store.createRole.bind(store),
    updateRole: store.updateRole.bind(store),
    deleteRole: store.deleteRole.bind(store),
  };
}
