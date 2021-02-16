import React from 'react';
import styled from 'styled-components';

const ConsentText = styled.p`
  font-size: 14px;
  color: #585858;
`;

export const Consent = (): React.ReactElement => {
  return (
    <ConsentText>
      Do you give your consent to UNICEF and its partners to view, edit and
      update your personal details and, if applicable, that of your household
      and dependants the purpose of the integrity UNICEFs beneficiary management
      system? Do you declare that the information you have provided is true and
      correct to the best of your knowledge?
    </ConsentText>
  );
};
