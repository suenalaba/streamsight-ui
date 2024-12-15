import React from 'react';
import Link from 'next/link';

interface CellLinkProps {
  label: string;
  href: string;
}

const CellLink = ({ label, href }: CellLinkProps) => {
  return <Link href={href} target="_blank" rel="noopener noreferrer">{label}</Link>;
};

export default CellLink;
