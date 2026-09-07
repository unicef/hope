import { createContext, ReactElement, ReactNode, useContext } from 'react';

const TimezoneContext = createContext<string>('UTC');

export const TimezoneProvider = ({
  timezone,
  children,
}: {
  timezone: string;
  children: ReactNode;
}): ReactElement => (
  <TimezoneContext.Provider value={timezone}>
    {children}
  </TimezoneContext.Provider>
);

export const useTimezone = (): string => useContext(TimezoneContext);
