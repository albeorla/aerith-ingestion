import { extendTheme } from "@chakra-ui/react";

const config = {
  initialColorMode: "light",
  useSystemColorMode: true,
};

const colors = {
  brand: {
    50: "#E5F0FF",
    100: "#B8D4FF",
    200: "#8AB9FF",
    300: "#5C9DFF",
    400: "#2E82FF",
    500: "#0066FF",
    600: "#0052CC",
    700: "#003D99",
    800: "#002966",
    900: "#001433",
  },
};

const semanticTokens = {
  colors: {
    "bg.canvas": {
      default: "gray.50",
      _dark: "gray.900",
    },
    "bg.surface": {
      default: "white",
      _dark: "gray.800",
    },
    "bg.subtle": {
      default: "gray.100",
      _dark: "gray.700",
    },
    "border.subtle": {
      default: "gray.200",
      _dark: "gray.700",
    },
    "text.primary": {
      default: "gray.900",
      _dark: "white",
    },
    "text.secondary": {
      default: "gray.600",
      _dark: "gray.400",
    },
    "text.tertiary": {
      default: "gray.500",
      _dark: "gray.300",
    },
  },
};

const theme = extendTheme({
  config,
  colors,
  semanticTokens,
  fonts: {
    heading: "var(--font-inter)",
    body: "var(--font-inter)",
  },
  shadows: {
    xs: "0 0 0 1px rgba(0, 0, 0, 0.05)",
    sm: "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
    md: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
    lg: "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
    xl: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
  },
  styles: {
    global: () => ({
      body: {
        bg: "bg.canvas",
        color: "text.primary",
        minH: "100vh",
      },
    }),
  },
  components: {
    Button: {
      baseStyle: {
        fontWeight: "medium",
        rounded: "lg",
        _hover: {
          transform: "translateY(-1px)",
          boxShadow: "sm",
        },
        _active: {
          transform: "translateY(0)",
        },
      },
      defaultProps: {
        colorScheme: "brand",
        size: "md",
      },
    },
    Card: {
      baseStyle: {
        container: {
          bg: "bg.surface",
          rounded: "xl",
          boxShadow: "sm",
          borderWidth: "1px",
          borderColor: "border.subtle",
          overflow: "hidden",
          transition: "all 0.2s",
          _hover: {
            boxShadow: "md",
            borderColor: "brand.200",
          },
        },
      },
      variants: {
        elevated: {
          container: {
            boxShadow: "md",
            borderWidth: "0",
            _hover: {
              boxShadow: "lg",
            },
          },
        },
        outline: {
          container: {
            boxShadow: "none",
          },
        },
      },
    },
    Table: {
      variants: {
        simple: {
          th: {
            borderBottom: "1px",
            borderColor: "border.subtle",
            color: "text.secondary",
            fontSize: "sm",
            fontWeight: "medium",
            textTransform: "none",
            letterSpacing: "normal",
            bg: "bg.subtle",
            py: 4,
            px: 6,
          },
          td: {
            borderBottom: "1px",
            borderColor: "border.subtle",
            fontSize: "sm",
            py: 4,
            px: 6,
          },
          tbody: {
            tr: {
              transition: "all 0.2s",
              _hover: {
                bg: "bg.subtle",
              },
            },
          },
        },
      },
    },
    Stat: {
      baseStyle: {
        container: {
          bg: "bg.surface",
          px: 6,
          py: 4,
        },
        label: {
          color: "text.secondary",
          fontSize: "sm",
          fontWeight: "medium",
          textTransform: "uppercase",
          letterSpacing: "wider",
        },
        number: {
          color: "text.primary",
          fontSize: "3xl",
          fontWeight: "bold",
          lineHeight: "tight",
        },
        helpText: {
          color: "text.tertiary",
          fontSize: "sm",
        },
      },
    },
    Badge: {
      baseStyle: {
        px: 2.5,
        py: 1,
        rounded: "md",
        fontSize: "xs",
        textTransform: "uppercase",
        fontWeight: "medium",
        letterSpacing: "wider",
        transition: "all 0.2s",
        _hover: {
          transform: "translateY(-1px)",
        },
      },
    },
  },
  layerStyles: {
    pageContainer: {
      maxW: "7xl",
      mx: "auto",
      px: { base: "4", md: "8", lg: "12" },
      py: { base: "6", md: "8", lg: "12" },
    },
  },
});

export default theme;
