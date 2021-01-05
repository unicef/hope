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
  canActivate: boolean;
  canEdit: boolean;
  canRemove: boolean;
  canFinish: boolean;
}

export function ProgramDetailsPageHeader({
  program,
  canActivate,
  canEdit,
  canRemove,
  canFinish,
}: ProgramDetailsPageHeaderPropTypes): React.ReactElement {
  let buttons;
  switch (program.status) {
    case ProgramStatus.Active:
      buttons = (
        <ActiveProgramDetailsPageHeaderButtons
          program={program}
          canFinish={canFinish}
          canEdit={canEdit}
        />
      );
      break;
    case ProgramStatus.Draft:
      buttons = (
        <DraftProgramDetailsPageHeaderButtons
          program={program}
          canRemove={canRemove}
          canEdit={canEdit}
          canActivate={canActivate}
        />
      );
      break;
    default:
      buttons = (
        <FinishedProgramDetailsPageHeaderButtons
          program={program}
          canActivate={canActivate}
        />
      );
  }
  const businessArea = useBusinessArea();
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Programme Management',
      to: `/${businessArea}/programs/`,
    },
  ];
  return (
    <PageHeader title={program.name} breadCrumbs={breadCrumbsItems}>
      {buttons}
    </PageHeader>
  );
}
