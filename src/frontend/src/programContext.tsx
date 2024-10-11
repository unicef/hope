import React, {
  createContext,
  ReactElement,
  useContext,
  useState,
} from 'react';
import { DataCollectingTypeType, ProgramStatus } from './__generated__/graphql';

export interface ProgramInterface {
  id: string;
  name: string;
  status: ProgramStatus;
  dataCollectingType: {
    id: string;
    householdFiltersAvailable: boolean;
    individualFiltersAvailable: boolean;
    label: string;
    code: string;
    type: string;
  };
  pduFields: { id: string }[];
}

export type ProgramContextType = ProgramInterface | null;

type ProgramContent = {
  selectedProgram: ProgramContextType;
  setSelectedProgram: (program: ProgramContextType) => void;
  isActiveProgram: boolean;
  isSocialDctType: boolean;
  isStandardDctType: boolean;
  programHasPdu: boolean;
};

export const ProgramContext = createContext(null);

export function ProgramProvider({
  children,
}: {
  children: React.ReactNode;
}): ReactElement {
  const [selectedProgram, setSelectedProgram] =
    useState<ProgramContextType>(null);
  let isActiveProgram = selectedProgram?.status === ProgramStatus.Active;
  const isSocialDctType =
    selectedProgram?.dataCollectingType?.type?.toUpperCase() ===
    DataCollectingTypeType.Social;
  const isStandardDctType =
    selectedProgram?.dataCollectingType?.type?.toUpperCase() ===
    DataCollectingTypeType.Standard;

  const programHasPdu = selectedProgram?.pduFields?.length > 0;

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
