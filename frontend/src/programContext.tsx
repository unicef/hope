import React, {
  createContext,
  ReactElement,
  useContext,
  useState,
} from 'react';
import { ProgramStatus } from './__generated__/graphql';

export interface ProgramInterface {
  id: string;
  name: string;
  status: ProgramStatus;
  individualDataNeeded: boolean;
  dataCollectingType: {
    id: string;
    householdFiltersAvailable: boolean;
    individualFiltersAvailable: boolean;
    label: string;
    code: string;
    type: string;
  };
}

export type ProgramContextType = ProgramInterface | null;

export const ProgramContext = createContext(null);

export const ProgramProvider = ({ children }): ReactElement => {
  const [selectedProgram, setSelectedProgram] = useState<ProgramContextType>(
    null,
  );
  let isActiveProgram = selectedProgram?.status === ProgramStatus.Active;

  //Set isActiveProgram to true if All Programs is selected
  if (selectedProgram === null) {
    isActiveProgram = true;
  }
  return (
    <ProgramContext.Provider
      value={{ selectedProgram, setSelectedProgram, isActiveProgram }}
    >
      {children}
    </ProgramContext.Provider>
  );
};

// eslint-disable-next-line @typescript-eslint/explicit-function-return-type
export const useProgramContext = () => useContext(ProgramContext);
