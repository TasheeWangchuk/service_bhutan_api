# jobs/helpers/notify.py
from job.models import  Proposal, Job
from notification.models import Notification
from user.models import CustomUser

def notify_user(user: CustomUser, message: str, notification_type: str, link: str = None):
    """
    Base notification function
    """
    return Notification.objects.create(
        user=user,
        message=message,
        notification_type=notification_type,
        link=link
    )

def notify_new_proposal(proposal: Proposal):
    """
    Notify job owner about new proposal
    """
    return notify_user(
        user=proposal.job.user,
        message=f"New proposal received for your job: {proposal.job.title}",
        notification_type='proposal',
        link=f"/jobs/{proposal.job.job_id}/proposals/{proposal.proposal_id}/"
    )

def notify_proposal_status_change(proposal: Proposal, old_status: str):
    """
    Notify freelancer about proposal status change
    """
    if proposal.status != old_status:
        return notify_user(
            user=proposal.user,
            message=f"Your proposal for {proposal.job.title} has been {proposal.status}",
            notification_type='proposal',
            link=f"/jobs/{proposal.job.job_id}/proposals/{proposal.proposal_id}/"
        )
    return None

def notify_job_status_change(job: Job, old_status: str):
    """
    Notify all proposal submitters about job status changes
    """
    if job.status != old_status:
        for proposal in job.proposals.all():
            notify_user(
                user=proposal.user,
                message=f"Job '{job.title}' status changed to {job.status}",
                notification_type='job',
                link=f"/jobs/{job.job_id}/"
            )

def notify_job_deletion(job: Job):
    """
    Notify all proposal submitters about job deletion
    """
    for proposal in job.proposals.all():
        notify_user(
            user=proposal.user,
            message=f"Job '{job.title}' has been deleted",
            notification_type='job',
            link="/jobs/"
        )