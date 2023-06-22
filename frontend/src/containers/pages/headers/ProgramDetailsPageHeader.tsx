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
}

export function ProgramDetailsPageHeader({
  program,
  canActivate,
  canEdit,
  canRemove,
  canFinish,
}: ProgramDetailsPageHeaderPropTypes): React.ReactElement {
  let buttons;
  const { t } = useTranslation();
  const { baseUrl, isAllPrograms } = useBaseUrl();
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
  const breadCrumbsItems: BreadCrumbsItem[] = [];
  if (isAllPrograms) {
    breadCrumbsItems.unshift({
      title: t('Programme Management'),
      to: `/${baseUrl}/list/`,
    });
  }

  return (
    <PageHeader title={program.name} breadCrumbs={breadCrumbsItems}>
      {buttons}
    </PageHeader>
  );
}
