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
import base64
import re
import glob
import pymysql
import yaml
from datetime import timedelta
import dateutil.parser
from athinaweb.athina_db import db_info


@login_required()
def index(request):
    assignments(request)


@login_required
def assignments(request):
    # TODO: incorporate paginator: https://docs.djangoproject.com/en/2.0/topics/pagination/
    # TODO: on delete should prompt a question that verifies by typing the name of the thing to be deleted
    assignments_list = Assignment.objects.filter(owner=request.user.id).order_by('-active', 'name')
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
def assignment_log(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    if assignment.owner != request.user.id:
        raise Http404
    else:
        list_of_files = glob.glob('%s/%s/*.log' % (settings.BASE_DIR, assignment.absolute_path))
        try:
            latest_file = os.path.basename(max(list_of_files, key=os.path.getctime))
        except ValueError:
            raise Http404
        return redirect('filemanager:view_file', inner_path="%s%s%s" % (assignment.name, "|", latest_file))


@login_required
def assignment_view(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    if assignment.owner != request.user.id:
        raise Http404
    else:
        # Security check passed
        try:
            conn = connect_to_db(assignment.absolute_path)
        except ValueError:
            return HttpResponse("No database found. Athina probably has not evaluated this assignment.<br />"
                                "Check the log file by viewing the directory to make sure that there are no"
                                "configuration errors.")
        cur = conn.cursor()
        # Get moss url (if it exists)
        course_id, assignment_id = get_course_assignment_id(request, assignment.absolute_path)
        cur.execute('SELECT variable_value FROM assignmentdata WHERE variable = %s AND '
                    'course_id = %s AND assignment_id = %s',
                    ('moss_url', course_id, assignment_id,))
        moss_url = cur.fetchone() if cur.fetchone() is not None else '#'

        cur.execute('SELECT user_id, user_fullname, secondary_id, repository_url, commit_date, last_graded,'
                    'last_grade, last_report, moss_max, moss_average, force_test FROM users WHERE '
                    '`course_id` = %s AND `assignment_id` = %s', (course_id, assignment_id,))
        users = []
        for user in cur.fetchall():
            if user[3] is None and user[6] is None:
                color = "table-danger"
                info = "No repository url submitted"
            elif user[10] == 1:
                color = "table-warning"
                info = "Forced test in progress"
            elif user[4] < user[5]:
                # graded
                color = "table-success"
                info = "Graded"
            else:
                # not grade or no url
                color = "table-warning"
                info = "Assignment not graded yet or past due date"
            users.append((user[0], user[1], user[2], color, info, user[6],
                          base64.b64encode(user[7]).decode("ascii"), user[8], user[9]))
        conn.close()
    return render(request, 'assignments/assignment_view.html', {"users": users, "users_len": len(users),
                                                                "assignment": assignment, "moss_url": moss_url})


def connect_to_db(absolute_path):
    db_details = db_info()
    return pymysql.connect(host=db_details.athina_mysql_host, user=db_details.athina_mysql_username,
                           password=db_details.athina_mysql_password, port=int(db_details.athina_mysql_port),
                           db="athina")


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
def get_course_assignment_id(request, absolute_path):
    with open('%s/%s/athina.yaml' % (settings.BASE_DIR, absolute_path), 'r') as stream:
        yaml_dict = yaml.load(stream, Loader=yaml.SafeLoader)
    return yaml_dict['course_id'], yaml_dict['assignment_id']


@login_required
def assignment_force(request, assignment_id, user_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    if assignment.owner != request.user.id:
        raise Http404
    else:
        # Revert the commit date on record to some older version. This will force Athina to think that it didn't check
        # the current commit. Also revert last_graded to an earlier date
        conn = connect_to_db(assignment.absolute_path)
        cur = conn.cursor()
        course_id, assignment_id = get_course_assignment_id(request, assignment.absolute_path)
        cur.execute("SELECT repository_url FROM users WHERE user_id=%s AND course_id=%s AND assignment_id=%s LIMIT 1",
                    (user_id, course_id, assignment_id,))
        result = cur.fetchone()
        repository_url = result if result is not None else '#'
        cur.execute("UPDATE users SET force_test=1 WHERE course_id=%s AND assignment_id=%s AND repository_url=%s",
                    (course_id, assignment_id, repository_url,))
        conn.commit()
        conn.close()
        return redirect('assignments:assignment_view', assignment_id=assignment.pk)


class APIView(generics.ListCreateAPIView):
    """This class defines the create behavior of our rest api."""
    queryset = Assignment.objects.filter(active=True)
    serializer_class = AssignmentListSerializer
