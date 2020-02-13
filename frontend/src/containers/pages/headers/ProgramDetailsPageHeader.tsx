import React from 'react';
import { ProgramNode, ProgramStatus } from '../../../__generated__/graphql';
import { PageHeader } from '../../../components/PageHeader';
import { BreadCrumbsItem } from '../../../components/BreadCrumbs';
import { useBusinessArea } from '../../../hooks/useBusinessArea';
import { FinishedProgramDetailsPageHeaderButtons } from './FinishedProgramDetailsPageHeaderButtons';
import { ActiveProgramDetailsPageHeaderButtons } from './ActiveProgramDetailsPageHeaderButtons';
import { DraftProgramDetailsPageHeaderButtons } from './DraftProgramDetailsPageHeaderButtons';

export interface ProgramDetailsPageHeaderPropTypes {
  program: ProgramNode;
}

export function ProgramDetailsPageHeader({
  program,
}: ProgramDetailsPageHeaderPropTypes): React.ReactElement {
  let buttons;
  switch (program.status) {
    case ProgramStatus.Active:
      buttons = <ActiveProgramDetailsPageHeaderButtons program={program} />;
      break;
    case ProgramStatus.Draft:
      buttons = <DraftProgramDetailsPageHeaderButtons program={program} />;
      break;
    default:
      buttons = <FinishedProgramDetailsPageHeaderButtons program={program} />;
  }
  const businessArea = useBusinessArea();
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Programme Managment',
      to: `/${businessArea}/programs/`,
    },
  ];
  return (
    <PageHeader title={program.name} breadCrumbs={breadCrumbsItems}>
      {buttons}
    </PageHeader>
  );
}
