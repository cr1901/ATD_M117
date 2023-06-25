use std::iter::repeat;
use std::path::Path;

use calm_io::*;
use clap::Parser;
use eyre::{eyre, Result};
use quine_mc_cluskey::Bool::{And, False, Not, Or, True};
use quine_mc_cluskey::*;

#[derive(clap::Parser)]
#[clap(author, version)]
///Minimize a system of boolean equations given a CSV file.
pub struct Args {
    /* #[clap(short = 'o')]
    /// output filename (defaults to stdout)
    pub out: Option<String>, */
    /// column (0-based) where outputs begin
    #[clap(short = 's')]
    pub split: u8,
    /// minimize outputs only for inputs where mask matches (0, 1, x for don't care)
    #[clap(short = 'm')]
    pub mask: Option<String>,
    /// input file name
    pub inp: String,
}

type MintermInfo = Vec<Bool>;

fn parse_mask<S>(mask_str: S, num_inputs: u8) -> Result<Vec<Bool>>
where
    S: IntoIterator<Item = char>,
{
    let mut mask_terms = Vec::<Bool>::new();

    for (i, c) in mask_str
        .into_iter()
        .chain(repeat('X'))
        .enumerate()
        .take_while(|(i, _)| i < &(num_inputs as usize))
    {
        match c {
            '0' => mask_terms.push(False),
            '1' => mask_terms.push(True),
            'X' | 'x' => mask_terms.push(Bool::Term(i as u8)),
            _ => return Err(eyre!("expecting '0', '1', 'X' or 'x' in mask string")),
        }
    }

    Ok(mask_terms)
}

fn parse_csv<P>(filename: P, out_idx: u8, inp_mask: Vec<Bool>) -> Result<MintermInfo>
where
    P: AsRef<Path>,
{
    let mut rdr = csv::Reader::from_path(filename)?;

    let mut output_exprs = Vec::<Bool>::new();
    let mut num_outputs = None;

    'next_term: for res in rdr.records() {
        let rec = res?;

        if num_outputs.is_none() {
            num_outputs = Some(rec.iter().skip(out_idx as usize).count());
            for _ in 0..num_outputs.unwrap() {
                output_exprs.push(Or(Vec::new()));
            }
        }

        let terms = rec
            .iter()
            .take(out_idx as usize)
            .enumerate()
            .map(|(i, s)| {
                s.parse::<u8>().map(|j| {
                    if j == 0 {
                        Not(Box::new(Bool::Term(i as u8)))
                    } else {
                        Bool::Term(i as u8)
                    }
                })
            })
            .collect::<Result<Vec<Bool>, _>>()?;

        // Make sure mask matches.
        for (t,m) in terms.iter().zip(inp_mask.iter()) {
            match (t, m) {
                (_, Bool::Term(_)) | (Bool::Not(_), Bool::False) | (Bool::Term(_), Bool::True) => continue,
                (_, _) => continue 'next_term
            }
        }

        let minterm = And(terms);
        let outputs_using_minterm = rec
            .iter()
            .skip(out_idx as usize)
            .enumerate()
            .filter_map(|(i, s)| {
                let parse_u8 = s.parse::<u8>();

                match parse_u8 {
                    Ok(j) if j == 0 => None,
                    e => Some(e.map(|_| i)),
                }
            })
            .collect::<Result<Vec<usize>, _>>()?;

        for idx in outputs_using_minterm {
            if let Or(ref mut v) = output_exprs[idx] {
                v.push(minterm.clone())
            } else {
                unreachable!()
            }
        }
    }

    Ok(output_exprs)
}

fn main() -> Result<()> {
    let args = Args::try_parse()?;

    let inp_mask = match args.mask {
        Some(s) => parse_mask(s.chars(), args.split)?,
        None => parse_mask(repeat('X'), args.split)?,
    };

    let output_exprs = parse_csv(args.inp, args.split, inp_mask)?;

    for expr in output_exprs {
        stdoutln!("{:?}", expr.simplify()).or_else(|e| match e.kind() {
            std::io::ErrorKind::BrokenPipe => Ok(()),
            _ => Err(e),
        })?;
    }

    Ok(())
}
