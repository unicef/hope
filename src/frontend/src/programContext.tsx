import {
  createContext,
  ReactElement,
  ReactNode,
  useContext,
  useState,
} from 'react';
import { DataCollectingTypeType, ProgramStatus } from './__generated__/graphql';
import { Program } from '@restgenerated/models/Program';
import { Status791Enum } from '@restgenerated/models/Status791Enum';

export interface ProgramInterface {
  id: string;
  name: string;
  status: ProgramStatus;
  programmeCode: string;
  slug: string;
  dataCollectingType: {
    id: string;
    householdFiltersAvailable: boolean;
    individualFiltersAvailable: boolean;
    label: string;
    code: string;
    type: string;
  };
  pduFields: { id: string }[];
  beneficiaryGroup: {
    id: string;
    name: string;
    groupLabel: string;
    groupLabelPlural: string;
    memberLabel: string;
    memberLabelPlural: string;
    masterDetail: boolean;
  };
}

export type ProgramContextType = Program | null;

type ProgramContent = {
  selectedProgram: Program;
  setSelectedProgram: (program: Partial<Program>) => void;
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
    selectedProgram?.data_collecting_type?.type?.toUpperCase() ===
    DataCollectingTypeType.Social;
  const isStandardDctType =
    selectedProgram?.data_collecting_type?.type?.toUpperCase() ===
    DataCollectingTypeType.Standard;

  const programHasPdu = selectedProgram?.pdu_fields?.length > 0;

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
