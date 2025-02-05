import React from 'react';
import { IconBrandYoutube, IconHome, IconSchool } from '@tabler/icons-react';
import { NavLink } from '@mantine/core';

const Navbar = () => {
  return (
    <>
      <NavLink
        href="/"
        label="Home"
        leftSection={<IconHome size="2rem" stroke={1.5} color="cyan" />}
      />
      <NavLink
        href="#required-for-focus"
        label="Stream Management"
        leftSection={<IconBrandYoutube size="2rem" stroke={1.5} color="cyan" />}
        childrenOffset={28}
      >
        <NavLink label="Stream Dashboard" href="/stream" />
        <NavLink label="Create Stream" href="/stream/create" />
      </NavLink>
      <NavLink
        href="/getting-started"
        label="Getting Started"
        leftSection={<IconSchool size="2rem" stroke={1.5} color="cyan" />}
      />
    </>
  );
};

export default Navbar;
