import React from 'react';
import { useTranslation } from 'react-i18next';
import { ProgramNode, ProgramStatus } from '../../../__generated__/graphql';
import { BreadCrumbsItem } from '../../../components/core/BreadCrumbs';
import { PageHeader } from '../../../components/core/PageHeader';
import { useBaseUrl } from '../../../hooks/useBaseUrl';
import { ActiveProgramDetailsPageHeaderButtons } from './ActiveProgramDetailsPageHeaderButtons';
import { DraftProgramDetailsPageHeaderButtons } from './DraftProgramDetailsPageHeaderButtons';
import { FinishedProgramDetailsPageHeaderButtons } from './FinishedProgramDetailsPageHeaderButtons';

export interface ProgramDetailsPageHeaderPropTypes {
  program: ProgramNode;
  canActivate: boolean;
  canEdit: boolean;
  canRemove: boolean;
  canFinish: boolean;
  canDuplicate: boolean;
}

export const ProgramDetailsPageHeader = ({
  program,
  canActivate,
  canEdit,
  canRemove,
  canFinish,
  canDuplicate,
}: ProgramDetailsPageHeaderPropTypes): React.ReactElement => {
  let buttons;
  const { t } = useTranslation();
  const { baseUrl } = useBaseUrl();
  switch (program.status) {
    case ProgramStatus.Active:
      buttons = (
        <ActiveProgramDetailsPageHeaderButtons
          program={program}
          canFinish={canFinish}
          canEdit={canEdit}
          canDuplicate={canDuplicate}
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
          canDuplicate={canDuplicate}
        />
      );
  }
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: t('Programme Management'),
      to: `/${baseUrl}/list/`,
    },
  ];

  return (
    <PageHeader title={program.name} breadCrumbs={breadCrumbsItems}>
      {buttons}
    </PageHeader>
  );
};
