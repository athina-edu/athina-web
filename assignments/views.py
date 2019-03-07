# from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Assignment
from .forms import AssignmentForm
import os
import shutil
from rest_framework import generics
from .serializers import AssignmentListSerializer
from django.contrib.auth.decorators import login_required
from django.http import Http404
import git
import html
import re


@login_required()
def index(request):
    assignments(request)


@login_required
def assignments(request):
    # TODO: incorporate paginator: https://docs.djangoproject.com/en/2.0/topics/pagination/
    # TODO: on delete should prompt a question that verifies by typing the name of the thing to be deleted
    assignments_list = Assignment.objects.filter(owner=request.user.id)
    return render(request, 'assignments/assignments.html',
                  {"assignments": assignments_list,
                   'assignments_len': len(assignments_list)})


@login_required
def assignment_create(request, **kwargs):
    """ View for creating and editing model Assignment using Assignment Form"""
    if request.method == "POST":
        assignment_id = kwargs.get('assignment_id', None)
        if assignment_id is not None:
            assignment = get_object_or_404(Assignment, pk=assignment_id)
            if assignment.owner != request.user.id:
                raise Http404
            form = AssignmentForm(request.POST, instance=assignment)
        else:
            form = AssignmentForm(request.POST)
        if form.is_valid():
            if form.instance.pk is None:  # New assignment, create folder
                assignment = form.save(commit=False)
                assignment.owner = request.user.id
                assignment.save()  # we have to save in order to get the pk
                assignment.absolute_path = "%s/%s/%s" % (settings.MEDIA_ROOT, request.user.id, assignment.name)
                assignment.save()
                if not os.path.exists(assignment.absolute_path):
                    os.makedirs(assignment.absolute_path)
                if assignment.git_password != "":
                    url_matches = re.findall("(.*?)://(.*?)$", assignment.git_source)
                    if url_matches[0][0] == 'https':
                        git_url = "%s://%s:%s@%s" % (url_matches[0][0],
                                                         html.escape(assignment.git_username),
                                                         html.escape(assignment.git_password),
                                                         url_matches[0][1])
                        git.Repo.clone_from(git_url, assignment.absolute_path)
                    else:
                        git.Repo.clone_from(assignment.git_source, assignment.absolute_path)
                else:
                    git.Repo.clone_from(assignment.git_source, assignment.absolute_path)
            else:  # Existing assignment, move folder
                old_assignment = get_object_or_404(Assignment, pk=assignment_id)
                assignment = form.save(commit=False)
                if old_assignment.name != assignment.name:
                    assignment.absolute_path = "%s/%s/%s" % (settings.MEDIA_ROOT, request.user.id, assignment.name)
                    shutil.move("%s/%s" % (settings.BASE_DIR, old_assignment.absolute_path),
                                "%s/%s" % (settings.BASE_DIR, assignment.absolute_path))
                assignment.save()
            os.chmod("%s/%s" % (settings.BASE_DIR, assignment.absolute_path), 0o777)
            return redirect('filemanager:index', inner_path="%s" % assignment.name)
    else:
        assignment_id = kwargs.get('assignment_id', None)
        if assignment_id is not None:
            assignment = get_object_or_404(Assignment, pk=assignment_id)
            if assignment.owner != request.user.id:
                raise Http404
            form = AssignmentForm(instance=assignment)
        else:
            form = AssignmentForm()
    return render(request, 'assignments/assignment_create.html', {'form': form})


# DEPRECATED
@login_required
def assignment_view(request, assignment_id):
    return render(request, 'assignments/assignment_view.html', {"assignment_id": assignment_id})


@login_required
def assignment_delete(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    if assignment.owner != request.user.id:
        raise Http404
    try:
        shutil.rmtree("%s/%s" % (settings.BASE_DIR, assignment.absolute_path))
    except FileNotFoundError:  # this error wont affect functionality
        pass
    assignment.delete()
    return redirect('assignments:assignments')


class APIView(generics.ListCreateAPIView):
    """This class defines the create behavior of our rest api."""
    queryset = Assignment.objects.filter(active=True)
    serializer_class = AssignmentListSerializer
