from flask import render_template, request, redirect, url_for, flash
import requests
from .forms import PokeForm
from app.blueprints.auth.models import Pokemon
from flask_login import login_required, current_user
from sqlalchemy import and_
from .import bp as main



@main.route('/pokeinfo', methods=['GET', 'POST'])
@login_required
def pokeinfo():
    form = PokeForm()
    if request.method == 'POST' and form.validate_on_submit():
        poke = request.form.get('poke_id')
        url = f"https://pokeapi.co/api/v2/pokemon/{poke}"        
        response = requests.get(url)
        if response.ok:            
            data = response.json()            
            poke_dict={
                'poke_name':data['name'],
                'base_hp':data['stats'][0]['base_stat'],
                'base_defense':data['stats'][2]['base_stat'],
                'base_attack':data['stats'][1]['base_stat'],                    
                'front_shiny':data["sprites"]["front_shiny"],
            }            
            flash(f"You found {poke_dict['poke_name']}!", 'success')
            return render_template('pokeinfo.html.j2', poke=poke_dict, form=form)        
        else:
            flash("That's not a Pokemon!", 'danger')
            return render_template('pokeinfo.html.j2', form=form)
    return render_template('pokeinfo.html.j2', form=form)

@main.route('/pokeget/<poke>', methods=['GET', 'POST'])
@login_required
def pokeget(poke):              
    url = f"https://pokeapi.co/api/v2/pokemon/{poke}"        
    response = requests.get(url)                   
    data = response.json()         
    poke_dict={
        'poke_name':data['name'],
        'base_hp':data['stats'][0]['base_stat'],
        'base_defense':data['stats'][2]['base_stat'],
        'base_attack':data['stats'][1]['base_stat'],                    
        'front_shiny':data["sprites"]["front_shiny"],
    }          
    pokemon = Pokemon.query.filter(and_(Pokemon.poke_name==poke, Pokemon.user_id==current_user.id)).all()    
    poke_count = Pokemon.query.filter(Pokemon.user_id==current_user.id).count()
    print(poke_count)
    if pokemon:        
        flash(f"You already caught {poke_dict['poke_name']}!", 'danger')
        return redirect(url_for('main.pokeinfo'))
    elif poke_count >= 5:
        flash("You have the max amount of Pokemon! Please remove some from your roster to add new Pokemon.", 'danger')
        return redirect(url_for('main.pokeinfo'))
    else:
        new_poke=Pokemon(user_id=current_user.id, poke_name=poke_dict['poke_name'], hit_points=poke_dict['base_hp'], defense=poke_dict['base_defense'], attack=poke_dict['base_attack'], poke_img=poke_dict['front_shiny'])
        new_poke.catch()
        flash(f"You caught {poke_dict['poke_name']}!", 'success')        
        return redirect(url_for('main.pokeinfo'))

@main.route('/pokeroster')
@login_required
def pokeroster():
    pokemon= Pokemon.query.all()
    return render_template('pokeroster.html.j2', pokemon = pokemon)

@main.route('/pokerelease/<int:id>')
@login_required
def pokerelease(id):
    poke_to_release = Pokemon.query.get(id)
    poke_to_release.release()
    flash(f"You have released a Pokemon!", 'danger')
    return redirect(url_for('main.pokeinfo'))

@main.route('/pokefight/<int:otherid>')
@login_required
def pokefight(otherid):
    pokemon= Pokemon.query.all()    
    return render_template('pokefight.html.j2', pokemon = pokemon, otherid = otherid)


@main.route('battle/<int:otherid>')
@login_required
def battle(otherid):
    your_attack = 0
    your_defense = 0
    their_attack = 0
    their_defense = 0    
    pokemon= Pokemon.query.all()
    for poke in pokemon:
        if poke.user_id == current_user.id:
            your_defense = your_defense + poke.hit_points + poke.defense
            your_attack = your_attack + poke.attack
        elif poke.user_id == otherid:
            their_defense = their_defense + poke.hit_points + poke.defense
            their_attack = their_attack + poke.attack
    your_score = your_defense - their_attack
    their_score = their_defense - your_attack
    if your_score > their_score:
        flash(f"You win!!! Final score: You = {your_score} | Them = {their_score}", 'success')
        return render_template('pokefight.html.j2', pokemon = pokemon, otherid = otherid)
    elif your_score < their_score:
        flash(f"You lost =( Final score: You = {your_score} | Them = {their_score}", 'danger')
        return render_template('pokefight.html.j2', pokemon = pokemon, otherid = otherid)
    else:
        flash(f"It's a tie! Final score: You = {your_score} | Them = {their_score}", 'warning')
        return render_template('pokefight.html.j2', pokemon = pokemon, otherid = otherid)
    