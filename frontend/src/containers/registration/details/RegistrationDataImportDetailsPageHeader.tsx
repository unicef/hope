import React from 'react';
import { RegistrationFragmentDetailedFragment, } from '../../../__generated__/graphql';
import { PageHeader } from '../../../components/PageHeader';
import { BreadCrumbsItem } from '../../../components/BreadCrumbs';
import { useBusinessArea } from '../../../hooks/useBusinessArea';

export interface RegistrationDataImportDetailsPageHeaderPropTypes {
  registration: RegistrationFragmentDetailedFragment;
}

export function RegistrationDataImportDetailsPageHeader({
  registration,
}: RegistrationDataImportDetailsPageHeaderPropTypes): React.ReactElement {
  // let buttons;
  // switch (program.status) {
  //   case ProgramStatus.Active:
  //     buttons = <ActiveProgramDetailsPageHeaderButtons program={program} />;
  //     break;
  //   case ProgramStatus.Draft:
  //     buttons = <DraftProgramDetailsPageHeaderButtons program={program} />;
  //     break;
  //   default:
  //     buttons = <FinishedProgramDetailsPageHeaderButtons program={program} />;
  // }
  const businessArea = useBusinessArea();
  const breadCrumbsItems: BreadCrumbsItem[] = [
    {
      title: 'Registration Data import',
      to: `/${businessArea}/registration-data-import/`,
    },
  ];
  return (
    <PageHeader title={registration.name} breadCrumbs={breadCrumbsItems} />
  );
}
