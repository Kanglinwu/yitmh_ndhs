
const routes = [
  {
    path: '/',
    component: () => import('layouts/handover.vue')
  },
  {
    path: '/kpiReview',
    component: () => import('pages/DHSMonitoringSystemPageSingle.vue')
  },
  {
    path: '/shiftleader',
    component: () => import('pages/DHSShiftLeaderPlanSinglePage.vue')
  },
  {
    path: '/search',
    component: () => import('pages/DHSSearchPageSingle.vue')
  },
  {
    path: '/incidentEventReview',
    component: () => import('pages/IncidentReview.vue')
  },
  {
    path: '/reviewPage/:_date/:_shift',
    component: () => import('pages/DHSReviewPage.vue')
  },
  {
    path: '/confirmPage',
    component: () => import('pages/DHSConfirmPage.vue')
  },
  {
    path: '/handover',
    component: () => import('layouts/handover.vue')
  },
  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/Error404.vue')
  }
]

export default routes
