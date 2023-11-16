import React, {createContext, ReactElement, useContext, useState} from "react";


enum ProgramStatus {
    DRAFT = "DRAFT",
    ACTIVE = "ACTIVE",
    FINISHED = "FINISHED"
}

export interface ProgramInterface {
    id: string,
    name: string,
    status: ProgramStatus,
    individualDataNeeded: boolean,
    dataCollectingType: {
        id: string,
        householdFiltersAvailable: boolean,
        individualFiltersAvailable: boolean
    }
}

export type ProgramContextType = ProgramInterface | null

export const ProgramContext = createContext(null);

export const ProgramProvider = ({ children }): ReactElement => {
    const [selectedProgram, setSelectedProgram] = useState<ProgramContextType>(null);

    return (
        <ProgramContext.Provider value={{ selectedProgram, setSelectedProgram }}>
            {children}
        </ProgramContext.Provider>
    )
}

export const useProgramContext = () => useContext(ProgramContext);