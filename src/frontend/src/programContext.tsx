import {
  createContext,
  ReactElement,
  ReactNode,
  useContext,
  useState,
} from 'react';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { Status791Enum } from '@restgenerated/models/Status791Enum';

export type ProgramContextType = Partial<ProgramDetail> | null;

type ProgramContent = {
  selectedProgram: Partial<ProgramDetail>;
  setSelectedProgram: (program: Partial<ProgramDetail>) => void;
  isActiveProgram: boolean;
  isSocialDctType: boolean;
  isStandardDctType: boolean;
  programHasPdu: boolean;
};

export const ProgramContext = createContext(null);

export function ProgramProvider({
  children,
}: {
  children: ReactNode;
}): ReactElement {
  const [selectedProgram, setSelectedProgram] =
    useState<ProgramContextType>(null);
  let isActiveProgram = selectedProgram?.status === Status791Enum.ACTIVE;
  const isSocialDctType =
    selectedProgram?.dataCollectingType?.type?.toUpperCase() === 'SOCIAL';
  const isStandardDctType =
    selectedProgram?.dataCollectingType?.type?.toUpperCase() === 'STANDARD';

  const programHasPdu =
    selectedProgram?.pduFields && selectedProgram.pduFields.length > 0;

  // Set isActiveProgram to true if All Programs is selected
  if (selectedProgram === null) {
    isActiveProgram = true;
  }
  return (
    <ProgramContext.Provider
      value={{
        selectedProgram,
        setSelectedProgram,
        isActiveProgram,
        isSocialDctType,
        isStandardDctType,
        programHasPdu,
      }}
    >
      {children}
    </ProgramContext.Provider>
  );
}

export const useProgramContext = (): ProgramContent =>
  useContext(ProgramContext);
