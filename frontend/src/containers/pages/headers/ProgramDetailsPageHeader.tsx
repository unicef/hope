import React from 'react';
import { FinishedProgramDetailsPageHeader } from './FinishedProgramDetailsPageHeader';
import { ActiveProgramDetailsPageHeader } from './ActiveProgramDetailsPageHeader';
import { DraftProgramDetailsPageHeader } from './DraftProgramDetailsPageHeader';
import { ProgramNode, ProgramStatus } from '../../../__generated__/graphql';

export interface ProgramDetailsPageHeaderPropTypes {
    program: ProgramNode;
}

export function ProgramDetailsPageHeader({
                                             program,
                                         }: ProgramDetailsPageHeaderPropTypes) {
    switch (program.status) {
        case ProgramStatus.Active:
            return <ActiveProgramDetailsPageHeader program={program}/>;
        case ProgramStatus.Draft:
            return <DraftProgramDetailsPageHeader program={program}/>;
        default:
            return <FinishedProgramDetailsPageHeader program={program}/>;
    }
}