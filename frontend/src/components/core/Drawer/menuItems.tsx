import { Assessment } from '@material-ui/icons';
import Assignment from '@material-ui/icons/Assignment';
import AttachMoney from '@material-ui/icons/AttachMoney';
import AutorenewIcon from '@material-ui/icons/AutorenewRounded';
import BallotIcon from '@material-ui/icons/Ballot';
import DashboardIcon from '@material-ui/icons/DashboardRounded';
import FaceIcon from '@material-ui/icons/Face';
import Feedback from '@material-ui/icons/Feedback';
import ForumIcon from '@material-ui/icons/Forum';
import InfoIcon from '@material-ui/icons/Info';
import ListIcon from '@material-ui/icons/List';
import NewReleases from '@material-ui/icons/NewReleases';
import ListAltRounded from '@material-ui/icons/ListAltRounded';
import LocalLibrary from '@material-ui/icons/LocalLibrary';
import MessageIcon from '@material-ui/icons/Message';
import PaymentIcon from '@material-ui/icons/Payment';
import PeopleAltRoundedIcon from '@material-ui/icons/PeopleAltRounded';
import PeopleIcon from '@material-ui/icons/PeopleRounded';
import QuestionAnswerIcon from '@material-ui/icons/QuestionAnswer';
import RateReviewIcon from '@material-ui/icons/RateReview';
import SupervisedUserCircle from '@material-ui/icons/SupervisedUserCircle';
import TrackChangesIcon from '@material-ui/icons/TrackChanges';
import TrendingUpRounded from '@material-ui/icons/TrendingUpRounded';
import React from 'react';
import { PERMISSIONS } from '../../../config/permissions';

export const menuItems = [
  {
    name: 'Country Dashboard',
    href: '/#',
    selectedRegexp: /^\/$/,
    icon: <DashboardIcon />,
    permissions: [PERMISSIONS.DASHBOARD_VIEW_COUNTRY],
  },
  {
    name: 'Registration Data Import',
    href: '/registration-data-import',
    selectedRegexp: /^\/registration-data-import.*$/,
    icon: <AutorenewIcon />,
    permissions: [PERMISSIONS.RDI_VIEW_DETAILS, PERMISSIONS.RDI_VIEW_LIST],
  },
  {
    name: 'Population',
    href: '/population/household',
    selectedRegexp: /^\/population.*$/,
    icon: <PeopleIcon />,
    collapsable: true,
    permissionModule: 'POPULATION',
    secondaryActions: [
      {
        name: 'Households',
        href: '/population/household',
        selectedRegexp: /^\/population\/household.*$/,
        icon: <PeopleAltRoundedIcon />,
        permissionModule: 'HOUSEHOLDS',
      },
      {
        name: 'Individuals',
        href: '/population/individuals',
        selectedRegexp: /^\/population\/individuals.*$/,
        icon: <FaceIcon />,
        permissionModule: 'INDIVIDUALS',
      },
    ],
  },
  {
    name: 'Programme Management',
    href: '/programs',
    selectedRegexp: /^\/programs.*$/,
    icon: <Assignment />,
    permissions: [
      PERMISSIONS.PRORGRAMME_VIEW_LIST_AND_DETAILS,
      PERMISSIONS.PROGRAMME_VIEW_PAYMENT_RECORD_DETAILS,
    ],
  },
  {
    name: 'Targeting',
    href: '/target-population',
    selectedRegexp: /^\/target-population.*$/,
    icon: <ListAltRounded />,
    permissions: [
      PERMISSIONS.TARGETING_VIEW_LIST,
      PERMISSIONS.TARGETING_VIEW_DETAILS,
    ],
  },
  {
    name: 'Cash Assist',
    selectedRegexp: /^\/unique.*$/,
    icon: <PaymentIcon />,
    external: true,
  },
  {
    name: 'Payment Module',
    href: '/payment-module',
    selectedRegexp: /^\/payment-module.*$/,
    icon: <PaymentIcon />,
    permissions: [PERMISSIONS.PM_VIEW_LIST, PERMISSIONS.PM_VIEW_DETAILS],
    flag: 'isPaymentPlanApplicable',
  },
  {
    name: 'Payment Verification',
    href: '/payment-verification',
    selectedRegexp: /^\/payment-verification.*$/,
    icon: <AttachMoney />,
    permissions: [
      PERMISSIONS.PAYMENT_VERIFICATION_VIEW_LIST,
      PERMISSIONS.PAYMENT_VERIFICATION_VIEW_DETAILS,
      PERMISSIONS.PAYMENT_VERIFICATION_VIEW_PAYMENT_RECORD_DETAILS,
    ],
  },
  {
    name: 'Grievance',
    href: '/grievance-and-feedback/tickets',
    selectedRegexp: /^\/grievance-and-feedback\/tickets.*$/,
    icon: <Feedback />,
    collapsable: true,
    permissionModule: 'GRIEVANCES',
    secondaryActions: [
      {
        name: 'Grievance Tickets',
        href: '/grievance-and-feedback/tickets/user-generated',
        selectedRegexp: /^\/grievance-and-feedback\/tickets.*$/,
        icon: <ListIcon />,
        permissionModule: 'GRIEVANCES',
      },
      {
        name: 'Grievance Dashboard',
        href: '/grievance-and-feedback/dashboard',
        selectedRegexp: /^\/grievance-and-feedback\/dashboard.*$/,
        icon: <Assessment />,
        permissionModule: 'GRIEVANCES',
      },
      {
        name: 'Feedback',
        href: '/accountability/feedback',
        selectedRegexp: /^\/accountability\/feedback.*$/,
        icon: <RateReviewIcon />,
        permissionModule: 'GRIEVANCES',
      },
    ],
  },
  {
    name: 'Accountability',
    href: '/accountability/communication',
    selectedRegexp: /^\/accountability\/communication.*$/,
    icon: <ForumIcon />,
    collapsable: true,
    permissionModule: 'ACCOUNTABILITY',
    flag: 'isAccountabilityApplicable',
    secondaryActions: [
      {
        name: 'Communication',
        href: '/accountability/communication',
        selectedRegexp: /^\/accountability\/communication.*$/,
        icon: <MessageIcon />,
        permissionModule: 'COMMUNICATION_MESSAGE',
      },
      {
        name: 'Feedback',
        href: '/accountability/feedback',
        selectedRegexp: /^\/accountability\/feedback.*$/,
        icon: <RateReviewIcon />,
        permissionModule: 'FEEDBACK',
      },
      {
        name: 'Surveys',
        href: '/accountability/surveys',
        selectedRegexp: /^\/accountability\/surveys.*$/,
        icon: <BallotIcon />,
        permissionModule: 'SURVEY',
      },
    ],
  },
  {
    name: 'Reporting',
    href: '/reporting',
    selectedRegexp: /^\/reporting.*$/,
    icon: <TrendingUpRounded />,
    permissions: [PERMISSIONS.REPORTING_EXPORT],
  },
  {
    name: 'Users',
    href: '/users-list',
    selectedRegexp: /^\/users-list.*$/,
    icon: <SupervisedUserCircle />,
    permissions: [PERMISSIONS.USER_MANAGEMENT_VIEW_LIST],
  },
  {
    name: 'Activity Log',
    href: '/activity-log',
    selectedRegexp: /^\/activity-log.*$/,
    icon: <TrackChangesIcon />,
    permissions: [PERMISSIONS.ACTIVITY_LOG_VIEW],
  },
];

export const resourcesItems = [
  {
    name: 'Knowledge Base',
    href:
      'https://unicef.service-now.com/cc?id=kb_search&kb_knowledge_base=be5501f9db003850d180f264f39619ee',
    icon: <LocalLibrary />,
  },
  {
    name: 'Conversations',
    href:
      'https://web.yammer.com/main/groups/eyJfdHlwZSI6Ikdyb3VwIiwiaWQiOiIxMzAzMTkwMDc3NDQifQ/all',
    icon: <QuestionAnswerIcon />,
  },
  {
    name: 'Tools and Materials',
    href: 'https://unicef.sharepoint.com/sites/EMOPS-HOPE',
    icon: <InfoIcon />,
  },
  {
    name: 'Release Note',
    href: '/api/changelog/',
    icon: <NewReleases />,
  },
];
