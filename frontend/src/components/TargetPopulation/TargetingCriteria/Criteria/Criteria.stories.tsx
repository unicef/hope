import React from 'react';
import { ThemeProvider } from '@material-ui/core';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { theme } from '../../../../theme';
import { Criteria } from './Criteria';

export default {
  component: Criteria,
  title: 'Criteria Card',
};

const EqualsCriteria:any = [{
  arguments: ["OTHER"],
  comparisionMethod: "EQUALS",
  isFlexField: false,
  fieldName: 'residence_status',
  fieldAttribute: {
    labelEn: 'Residence Status',
    name: 'residence_status',
    type: 'SELECT_ONE',
    choices: [{
      value: 'OTHER',
      labelEn: "Other",
    }]
  }
}]

export const CriteriaCardDisplay = () => {
  return (
    <ThemeProvider theme={theme}>
      <StyledThemeProvider theme={theme}>
        <Criteria rules={EqualsCriteria} isEdit={true} canRemove={false} />
      </StyledThemeProvider>
    </ThemeProvider>
  );
};
