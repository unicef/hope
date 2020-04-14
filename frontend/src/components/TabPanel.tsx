import React from 'react';

interface TabPanelProps {
  children: React.ReactNode;
  index: number;
  value: number;
}
export function TabPanel({
  children,
  index,
  value,
}: TabPanelProps): React.ReactElement {
  const style = {};
  if (index !== value) {
    // eslint-disable-next-line dot-notation
    style['display'] = 'none';
  }
  return <div style={style}>{children}</div>;
}
