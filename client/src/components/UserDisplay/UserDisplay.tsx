'use client';

import { forwardRef, useEffect } from 'react';
import { IconChevronRight, IconLogout } from '@tabler/icons-react';
import { Avatar, Button, Group, Menu, rem, Text, UnstyledButton } from '@mantine/core';
import { createClient } from '../../../utils/supabase/client';
import { login } from '../../login';
import { useAuth } from '../../providers/AuthProvider';

interface UserButtonProps extends React.ComponentPropsWithoutRef<'button'> {
  image: string;
  name: string;
  email: string;
  icon?: React.ReactNode;
}

const UserButton = forwardRef<HTMLButtonElement, UserButtonProps>(
  ({ image, name, email, icon, ...others }: UserButtonProps, ref) => (
    <UnstyledButton
      ref={ref}
      style={{
        color: 'var(--mantine-color-text)',
        borderRadius: 'var(--mantine-radius-sm)',
      }}
      {...others}
    >
      <Group>
        <Avatar src={image} radius="xl" />

        <div style={{ flex: 1 }}>
          <Text size="sm" fw={500}>
            {name}
          </Text>

          <Text c="dimmed" size="xs">
            {email}
          </Text>
        </div>

        {icon || <IconChevronRight size="1rem" />}
      </Group>
    </UnstyledButton>
  )
);

function getUsernameFromEmail(email: string) {
  return email.split('@')[0];
}

const UserDisplay = () => {
  const { userEmail, setUserEmail, logout } = useAuth();

  useEffect(() => {
    const retrieveUserEmail = async () => {
      if (userEmail) {
        return;
      }
      const supabase = createClient();
      const {
        data: { user },
      } = await supabase.auth.getUser();
      if (user) {
        setUserEmail(user.email!);
      }
    };
    retrieveUserEmail();
  }, [userEmail]);
  return (
    <>
      {userEmail ? (
        <Menu withArrow>
          {/* @ts-ignore */}
          <Menu.Target>
            <UserButton
              image="https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/avatars/avatar-8.png"
              name={getUsernameFromEmail(userEmail)}
              email={userEmail}
            />
          </Menu.Target>
          <Menu.Dropdown>
            <Menu.Label>Welcome {getUsernameFromEmail(userEmail)}</Menu.Label>
            <Menu.Item
              color="red"
              leftSection={<IconLogout style={{ width: rem(14), height: rem(14) }} />}
              onClick={logout}
            >
              Sign out
            </Menu.Item>
          </Menu.Dropdown>
        </Menu>
      ) : (
        <Button onClick={login} variant="filled" color="rgba(0, 61, 245, 1)">
          Login
        </Button>
      )}
    </>
  );
};

export default UserDisplay;
