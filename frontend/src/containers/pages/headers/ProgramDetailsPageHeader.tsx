import React from 'react';
import { ProgramNode, ProgramStatus } from '../../../__generated__/graphql';
import { FinishedProgramDetailsPageHeader } from './FinishedProgramDetailsPageHeader';
import { ActiveProgramDetailsPageHeader } from './ActiveProgramDetailsPageHeader';
import { DraftProgramDetailsPageHeader } from './DraftProgramDetailsPageHeader';

export interface ProgramDetailsPageHeaderPropTypes {
    program: ProgramNode;
}

export function ProgramDetailsPageHeader({
                                             program,
                                         }: ProgramDetailsPageHeaderPropTypes):React.ReactElement {
    switch (program.status) {
        case ProgramStatus.Active:
            return <ActiveProgramDetailsPageHeader program={program}/>;
        case ProgramStatus.Draft:
            return <DraftProgramDetailsPageHeader program={program}/>;
        default:
            return <FinishedProgramDetailsPageHeader program={program}/>;
    }
}