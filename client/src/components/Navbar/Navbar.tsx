import { NavLink } from '@mantine/core';
import { IconBrandYoutube } from '@tabler/icons-react';
import React from 'react'

const Navbar = () => {
  return (
    <>
      <NavLink
        href="#required-for-focus"
        label="Stream Management"
        leftSection={<IconBrandYoutube size="2rem" stroke={1.5} color="cyan"/>}
        childrenOffset={28}
      >
        <NavLink label="Stream Dashboard" href="#required-for-focus" />
        <NavLink label="Stream Information" href="#required-for-focus" />
        <NavLink label="Create Stream" href="#required-for-focus" />
      </NavLink>
    </>
  );
}

export default Navbar;
