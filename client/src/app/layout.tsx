import '@mantine/core/styles.css';
import '@mantine/notifications/styles.css';

import { AllCommunityModule, ModuleRegistry } from 'ag-grid-community';
import {
  AppShell,
  AppShellHeader,
  AppShellMain,
  AppShellNavbar,
  ColorSchemeScript,
  Group,
  MantineProvider,
  Text,
} from '@mantine/core';
import { Notifications } from '@mantine/notifications';
import Navbar from '@/components/Navbar/Navbar';

ModuleRegistry.registerModules([AllCommunityModule]);

export const metadata = {
  title: 'My Mantine app',
  description: 'I have followed setup instructions carefully',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <ColorSchemeScript />
      </head>
      <body>
        <MantineProvider>
          <Notifications />
          <AppShell
            header={{ height: 60 }}
            navbar={{
              width: 300,
              breakpoint: 'sm',
            }}
            padding="md"
          >
            <AppShellHeader>
              <Group h="100%" px="md">
                <Text
                  size="xl"
                  fw={900}
                  variant="gradient"
                  gradient={{ from: '#1c7ed6', to: '#22b8cf' }}
                >
                  Streamsight-UI
                </Text>
              </Group>
            </AppShellHeader>
            <AppShellNavbar p="md">
              <Navbar />
            </AppShellNavbar>
            <AppShellMain>{children}</AppShellMain>
          </AppShell>
        </MantineProvider>
      </body>
    </html>
  );
}
