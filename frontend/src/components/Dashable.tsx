import React, {ReactElement} from 'react';

export function Dashable({
  value,
  children,
  div = true,
  className,
}: {
  value?: string | number | null | undefined;
  children?: string | number | null | undefined;
  className?;
  div?: boolean;
}): ReactElement {
  let instance = value;
  if (value === null || value === undefined) {
    instance = children;
  }
  if (div) {
    if (instance === null || instance === undefined || instance === '') {
      return <div className={className}>-</div>;
    }
    return <div className={className}>{instance}</div>;
  }
  if (instance === null || instance === undefined || instance === '') {
    return <>-</>;
  }
  return <>{instance}</>;
}
