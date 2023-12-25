import json
import subprocess
from PyInquirer import prompt, style_from_dict, Token
import webbrowser


custom_style = style_from_dict({
    Token.QuestionMark: '#00B8D9 bold',
    Token.Selected: '#31A5A9 bold',
    Token.Instruction: '',  # no styling
    Token.Answer: '#3F8AB8 bold',
    Token.Question: '',
})

members_cache = {}
prs_cache = {}

def grevlist(repo):
    """Run the gh pr list command and return the parsed output."""
    try:
        output = subprocess.check_output(
            ['gh', 'pr', 'list', '-R', repo, '--json', 'number,reviewRequests'],
            universal_newlines=True
        )
        pr_data = json.loads(output)
        unique_prs = {}
        for pr in pr_data:
            if 'reviewRequests' in pr:
                for request in pr['reviewRequests']:
                    if 'login' in request:
                        member = request['login']
                        pr_number = pr['number']
                        if member not in unique_prs:
                            unique_prs[member] = set()
                        unique_prs[member].add(pr_number)
        return unique_prs
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        return {}

def display_pr_titles(member, repos):
    """Return PR titles and URLs for a selected member with repo names."""
    if member not in prs_cache:
        prs_cache[member] = []
        for repo in repos:
            try:
                output = subprocess.check_output(
                    ['gh', 'pr', 'list', '-R', repo, '--json', 'title,url,reviewRequests'],
                    universal_newlines=True
                )
                pr_data = json.loads(output)
                for pr in pr_data:
                    review_requests = pr.get('reviewRequests', [])
                    if any(member == request.get('login') for request in review_requests):
                        pr_title = f"{repo}: {pr['title']}"
                        prs_cache[member].append({'name': pr_title, 'value': pr['url']})
            except subprocess.CalledProcessError as e:
                print(f"An error occurred while fetching PRs for {repo}: {e}")
    return prs_cache[member]


def get_member_choices(repos):
    """Fetch, cache, and sort the list of members with their PR counts."""
    if not members_cache:
        all_prs = {}
        for repo in repos:
            repo_prs = grevlist(repo)
            for member, pr_numbers in repo_prs.items():
                if member not in all_prs:
                    all_prs[member] = set()
                all_prs[member].update(pr_numbers)
        for member, prs in all_prs.items():
            members_cache[member] = len(prs)

    sorted_members = sorted(members_cache, key=members_cache.get, reverse=True)
    return [{'name': f'{member} {members_cache[member]}', 'value': member} for member in sorted_members]


def main():
    while True:
        repo_file = 'repos.txt'
        repos = []
        try:
            with open(repo_file, 'r') as file:
                repos = [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            print(f"Repository file '{repo_file}' not found.")
            return
        member_choices = get_member_choices(repos=repos)
        member_choices.append({'name': 'Exit', 'value': 'exit'})

        member_question = [{
            'type': 'list',
            'name': 'team_member',
            'message': 'Select a team member:',
            'choices': member_choices
        }]

        try:
            member_answer = prompt(member_question, style=custom_style)
        except Exception as e:
            print("An error occurred. Please use keyboard navigation.")


        if member_answer['team_member'] == 'exit':
            print("Exiting the application.")
            break

        pr_choices = display_pr_titles(member_answer['team_member'], ['Medsien/medsien-api', 'Medsien/medsien-web', 'Medsien/medsien-ehr-etl'])
        if pr_choices:
            # Temporarily add 'Go Back' option for this display
            display_choices = pr_choices + [{'name': 'Go Back', 'value': 'back'}]
            pr_question = [{
                'type': 'list',
                'name': 'pr_url',
                'message': 'Select a PR to view details or Go Back:',
                'choices': display_choices
            }]
            pr_answer = prompt(pr_question, style=custom_style)
            if pr_answer['pr_url'] == 'back':
                continue  # Go back to the member list
            else:
                print(f"Opening PR: {pr_answer['pr_url']}")
                webbrowser.open(pr_answer['pr_url'])
        else:
            print(f"No PRs found for {member_answer['team_member']}.")

if __name__ == '__main__':
    main()