# from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.http import HttpResponse
from .models import Assignment
from .forms import AssignmentForm
import os
import shutil
from rest_framework import generics
from .serializers import AssignmentListSerializer
import git
import html
import re
import glob
import sqlite3
from datetime import timedelta
import dateutil.parser


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


@login_required
def assignment_view(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    if assignment.owner != request.user.id:
        raise Http404
    else:
        # Security check passed
        # Find the latest sqlite3 file and open it
        try:
            conn = connect_to_sqlite(assignment.absolute_path)
        except ValueError:
            return HttpResponse("No sqlite3 database found. Athina probably has not evaluated this assignment.<br />"
                                "Check the log file by viewing the directory to make sure that there are no"
                                "configuration errors.")
        cur = conn.cursor()
        cur.execute('SELECT user_id, user_fullname, secondary_id, repository_url, commit_date, last_graded FROM users')
        users = []
        for user in cur.fetchall():
            if user[3] is None:
                color = "table-danger"
                info = "No repository url submitted."
            elif user[4] < user[5]:
                # graded
                color = "table-success"
            else:
                # not grade or no url
                color = "table-warning"
                info = "Assignment not graded yet or unable to grade."
            users.append((user[0], user[1], user[2], color, info))
        conn.close()
    return render(request, 'assignments/assignment_view.html', {"users": users, "users_len": len(users),
                                                                "assignment": assignment})


def connect_to_sqlite(absolute_path):
    list_of_files = glob.glob('%s/%s/*.sqlite3' % (settings.BASE_DIR, absolute_path))
    latest_file = max(list_of_files, key=os.path.getctime)
    conn = sqlite3.connect(latest_file)
    return conn


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


@login_required
def assignment_force(request, assignment_id, user_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    if assignment.owner != request.user.id:
        raise Http404
    else:
        # Revert the commit date on record to some older version. This will force Athina to think that it didn't check
        # the current commit. Also revert last_graded to an earlier date
        conn = connect_to_sqlite(assignment.absolute_path)
        cur = conn.cursor()
        cur.execute('SELECT commit_date, last_graded FROM users WHERE user_id=?', (user_id,))
        row = cur.fetchone()
        # TODO: convert dates to str and the vice versa
        try:
            commit_date = dateutil.parser.parse(row[0]) - timedelta(days=1)
            last_graded = commit_date - timedelta(days=1)
        except OverflowError:
            # Date is the earliest possible, 1-1-1
            commit_date = dateutil.parser.parse(row[0]) + timedelta(days=1)
            last_graded = commit_date - timedelta(days=1)
        cur.execute("UPDATE users SET commit_date=?, last_graded=? WHERE user_id=?",
                    (commit_date, last_graded, user_id,))
        conn.commit()
        conn.close()
        return redirect('assignments:assignment_view', assignment_id=assignment.pk)


class APIView(generics.ListCreateAPIView):
    """This class defines the create behavior of our rest api."""
    queryset = Assignment.objects.filter(active=True)
    serializer_class = AssignmentListSerializer
